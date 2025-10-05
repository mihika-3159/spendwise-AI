# app.py
import os
import secrets
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

from utils.data_utils import (
    read_users, write_user, verify_user_credentials, get_user_role,
    is_user_activated, set_user_activation, get_activation_code,
    log_expense, expenses_df, totals_by_category, total_spent_month,
    write_feedback, read_feedback
)
from utils.tips import get_ai_tip, generate_tip
from utils.config import CATEGORIES

load_dotenv()

# SMTP config (optional)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587") or 587)
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)

st.set_page_config(page_title="Spendwise", page_icon="💸", layout="centered")

# ---- UI helpers ----
def send_activation_email(to_email: str, username: str, activation_code: str):
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        return False, "SMTP not configured"
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Spendwise - Activate your account'
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg.set_content(f"Hi {username},\n\nYour Spendwise activation code is: {activation_code}\n\nEnter this code in the app to activate your account.")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True, "Email sent"
    except Exception as e:
        return False, str(e)

def generate_activation_code():
    return secrets.token_hex(3)

def strong_password_ok(password: str):
    if len(password) < 8:
        return False, "At least 8 characters required."
    if password.lower() == password:
        return False, "Include an uppercase letter."
    if password.upper() == password:
        return False, "Include a lowercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Include a number."
    return True, ""

def login_and_reload(username: str):
    st.session_state['user'] = username
    st.session_state['role'] = get_user_role(username)
    st.rerun()

def logout_and_reload():
    st.session_state.pop('user', None)
    st.session_state.pop('role', None)
    st.rerun()

# ---- Auth pages ----
def login_page():
    st.title("💸 Spendwise — Login")
    st.write("Smart tracking, personalized AI tips.")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login", key="login_btn"):
        users = read_users()

        # Demo shortcut
        if username == "demo" and password == "demo123":
            if username in users:
                login_and_reload(username)
            else:
                st.error("Demo account missing. Run demo_fixtures.py.")
            return

        # Admin shortcut
        if username == "admin" and password == "admin123":
            if username in users:
                login_and_reload(username)
            else:
                st.error("Admin account missing. Run demo_fixtures.py.")
            return

        # Normal users
        if username not in users:
            st.error("User not found. Please register.")
            return

        if not is_user_activated(username):
            st.warning("Account not activated. Activate from email.")
            return

        if verify_user_credentials(username, password):
            login_and_reload(username)
        else:
            st.error("Invalid credentials.")

def register_page():
    st.header("Register")
    username = st.text_input("Choose username", key="reg_user")
    email = st.text_input("Email (for activation)", key="reg_email")
    password = st.text_input("Choose password", type="password", key="reg_pass")
    purpose = st.text_input("Short purpose / goal (optional)", key="reg_purpose")
    goal = st.number_input("Monthly saving goal ($)", min_value=0.0, value=0.0, key="reg_goal")
    if st.button("Create account", key="reg_btn"):
        if not username or not email or not password:
            st.error("Username, email and password required.")
            return
        users = read_users()
        if username in users:
            st.error("Username exists.")
            return
        ok, reason = strong_password_ok(password)
        if not ok:
            st.error(f"Weak password: {reason}")
            return
        activation_code = generate_activation_code()
        write_user({
            "username": username,
            "password": password,
            "purpose": purpose,
            "goal": goal,
            "role": "user",
            "activated": False,
            "activation_code": activation_code,
            "email": email
        })
        ok_email, msg = send_activation_email(email, username, activation_code)
        if ok_email:
            st.success("Account created. Activation code sent to your email.")
        else:
            st.warning(f"Account created but failed to send email: {msg}. Activation code: {activation_code}")
        # set session pending activation so app redirects to activation page
        st.session_state['pending_activation'] = username
    st.rerun()

def activation_page():
    st.header("Activate your account")
    pending = st.session_state.get('pending_activation', '')
    st.write(f"Activating: **{pending}**")
    code = st.text_input("Enter activation code", key="act_code")
    if st.button("Activate", key="act_btn"):
        expected = get_activation_code(pending)
        if code.strip() and expected and code.strip() == expected:
            set_user_activation(pending, True)
            st.success("Activated! Please login now.")
            st.session_state.pop('pending_activation', None)
            st.rerun()
        else:
            st.error("Invalid code. Check your email or the activation code shown in the app (for testing).")

# ---- Core app parts (post-login) ----
def topbar(username: str):
    c1, c2 = st.columns([10,1])
    with c1:
        st.markdown(f"**Logged in as:** `{username}`")
    with c2:
        if st.button("🔒 Logout", key="logout_btn"):
            logout_and_reload()

def profile_page(username: str):
    st.header("Profile & Goal")
    users = read_users()
    u = users.get(username, {})
    st.write(f"**Purpose:** {u.get('purpose','')}")
    st.write(f"**Email:** {u.get('email','')}")
    curr_goal = float(u.get('goal',0.0))
    st.write(f"**Current monthly goal:** ${curr_goal:.2f}")
    new_goal = st.number_input("Change monthly saving goal", min_value=0.0, value=curr_goal, step=10.0, key=f"goal_{username}")
    if st.button("Save goal", key=f"save_goal_{username}"):
        u['goal'] = float(new_goal)
        write_user(u)
        st.success("Goal updated.")
    st.rerun()

def expenses_page(username: str):
    st.header("Log Expense")
    date = st.date_input("Date", value=pd.Timestamp.today().date(), key=f"date_{username}")
    category = st.selectbox("Category", CATEGORIES, key=f"cat_{username}")
    amount = st.number_input("Amount ($)", min_value=0.0, step=0.01, key=f"amt_{username}")
    desc = st.text_input("Description", key=f"desc_{username}")
    if st.button("Add Expense", key=f"add_{username}"):
        try:
            log_expense(username, str(date), category, float(amount), desc)
            st.success("Logged.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed: {e}")
    st.markdown("---")
    df = expenses_df(username)
    if df.empty:
        st.info("No expenses yet.")
    else:
        st.subheader("Your expenses")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇ Export expenses CSV", data=csv, file_name=f"{username}_expenses.csv", mime="text/csv")
        # analytics
        month_start = pd.Timestamp.today().replace(day=1).date()
        total = total_spent_month(username, month_start)
        users = read_users()
        goal = float(users.get(username, {}).get('goal',0.0))
        c1,c2 = st.columns(2)
        c1.metric("Spent this month", f"${total:.2f}")
        c2.metric("Goal", f"${goal:.2f}")
        if st.button("Show graphs", key=f"graphs_{username}"):
            totals = totals_by_category(username, since_date=month_start)
            if totals:
                cats = list(totals.keys()); vals = [totals[k] for k in cats]
                col1,col2 = st.columns(2)
                with col1:
                    fig, ax = plt.subplots(figsize=(5,3))
                    ax.bar(cats, vals)
                    ax.set_title("Spending by category (this month)")
                    plt.xticks(rotation=30)
                    st.pyplot(fig)
                with col2:
                    fig2, ax2 = plt.subplots(figsize=(4,4))
                    ax2.pie(vals, labels=cats, autopct="%1.1f%%", startangle=90)
                    ax2.set_title("Spending distribution")
                    st.pyplot(fig2)
            else:
                st.info("No data for graphs.")

from utils.tips import get_ai_tip

def tips_page(username: str):
    st.header("💡 Personalized AI Tip")
    st.write("Get a short, practical money-saving suggestion based on your last 30 days of spending.")

    if st.button("✨ Get Personalized Tip", key=f"tip_{username}"):
        with st.spinner("Thinking..."):
            try:
                tip = get_ai_tip(username)
                if "AI unavailable" in tip or "Error" in tip:
                    st.warning("⚠️ AI unavailable, showing fallback tip.")
                    st.success(generate_tip())
                else:
                    st.success(tip)
            except Exception as e:
                st.error(f"Failed to fetch tip: {e}")
                st.success(generate_tip())

def feedback_page(username: str):
    st.header("Send feedback")
    with st.form("fb_form", clear_on_submit=True):
        rating = st.slider("Rating (1-5)", min_value=1, max_value=5, value=5)
        text = st.text_area("Your feedback")
        submitted = st.form_submit_button("Submit")
        if submitted:
            if not text.strip():
                st.warning("Enter feedback text.")
            else:
                write_feedback(username, text.strip(), rating)
                st.success("Thanks for your feedback!")

def admin_feedback_view():
    st.header("Admin - Feedback")
    rows = read_feedback()
    if not rows:
        st.info("No feedback yet.")
        return
    df = pd.DataFrame(rows)
    if 'timestamp' not in df.columns:
        df['timestamp'] = ""
    try:
        df['ts'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.sort_values('ts', ascending=False)
    except Exception:
        pass
    st.dataframe(df.drop(columns=['ts'], errors='ignore'))
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇ Export feedback CSV", data=csv, file_name="feedback.csv", mime="text/csv")

def admin_users_view():
    st.header("Admin - Users")
    users = read_users()
    df = pd.DataFrame([u for u in users.values()])
    st.dataframe(df)
    # export
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇ Export users CSV", data=csv, file_name="users.csv", mime="text/csv")

# ---- Main behavior ----
def main():
    # seed demo users if no users exist (only on first run)
    if not read_users():
        try:
            import demo_fixtures
            demo_fixtures.seed_demo()
        except Exception:
            pass

    # --- Auth flow ---
    if 'user' not in st.session_state and 'pending_activation' not in st.session_state:
        # hide sidebar on login/register
        st.sidebar.empty()
        login_page()
        st.markdown("---")
        st.header("Register")
        register_page()
        return

    elif 'pending_activation' in st.session_state:
        st.sidebar.empty()
        activation_page()
        return

    # --- Logged in ---
    username = st.session_state['user']
    role = st.session_state.get('role', get_user_role(username))
    topbar(username)

    # Sidebar only appears when logged in
    nav_items = {
        "Home": "🏠 Home",
        "Log Expense": "➕ Log Expense",
        "AI Tip": "💡 AI Tip",
        "Feedback": "✉️ Feedback",
        "Profile": "⚙️ Profile"
    }

    if role == 'admin':
        nav_items.update({
            "Admin Feedback": "🗂️ Admin Feedback",
            "Admin Users": "👥 Admin Users"
        })

    choice = st.sidebar.radio("Navigate", list(nav_items.values()))
    selected_page = [k for k, v in nav_items.items() if v == choice][0]

    # --- Routing ---
    if selected_page == "Home":
        st.title("Spendwise Dashboard")
        df = expenses_df(username)
        if df.empty:
            st.info("No expenses — add one.")
        else:
            st.subheader("Recent expenses")
            st.dataframe(df.sort_values(by='date', ascending=False).head(5))

    elif selected_page == "Log Expense":
        expenses_page(username)

    elif selected_page == "AI Tip":
        tips_page(username)

    elif selected_page == "Feedback":
        feedback_page(username)

    elif selected_page == "Profile":
        profile_page(username)

    elif selected_page == "Admin Feedback" and role == 'admin':
        admin_feedback_view()

    elif selected_page == "Admin Users" and role == 'admin':
        admin_users_view()

if __name__ == "__main__":
    main()