# app.py
import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

from utils.data_utils import (
    read_users, write_user, verify_user_credentials, get_user_role,
    log_expense, expenses_df, totals_by_category, total_spent_month,
    write_feedback, read_feedback
)
from utils.tips import generate_tip
from utils import CATEGORIES

st.set_page_config(page_title="Spendwise", page_icon="💸", layout="centered")

# -------------------------
# Authentication UI
# -------------------------
def login_register_ui():
    st.title("💸 Spendwise - Smart Expense Tracker")
    st.write("Track expenses, set goals, get AI tips, and give feedback.")
    menu = ["Login", "Register", "Demo Seed"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login to your account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if verify_user_credentials(username, password):
                st.session_state["user"] = username
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid username or password.")

    elif choice == "Register":
        st.subheader("Create a new account")
        username = st.text_input("Choose a username", key="reg_username")
        password = st.text_input("Choose a password", type="password", key="reg_password")
        purpose = st.text_input("What is your financial goal?", key="reg_purpose")
        goal = st.number_input("Monthly saving goal ($)", min_value=0.0, value=0.0, key="reg_goal")
        if st.button("Register"):
            users = read_users()
            if not username:
                st.warning("Please enter a username.")
            elif username in users:
                st.warning("Username already exists.")
            else:
                write_user({
                    "username": username,
                    "password": password,
                    "purpose": purpose,
                    "goal": goal,
                    "role": "user"
                })
                st.success("Account created successfully! Please log in.")

    elif choice == "Demo Seed":
        st.subheader("Seed Demo Data")
        st.write("Click to seed demo user and sample data (demo/demo123, admin/admin123).")
        if st.button("Seed Demo Data"):
            try:
                import demo_fixtures
                demo_fixtures.seed_demo()
                st.success("Demo data seeded. Use demo/demo123 to login or admin/admin123 to view feedback.")
            except Exception as e:
                st.error(f"Error seeding demo data: {e}")

# -------------------------
# Expense UI
# -------------------------
def expense_ui(username):
    st.header("Log Expenses")
    date = st.date_input("Date", datetime.date.today())
    category = st.selectbox("Category", CATEGORIES)
    amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
    description = st.text_input("Description")
    if st.button("Add Expense"):
        try:
            log_expense(username, str(date), category, amount, description)
            st.success("Expense logged!")
        except Exception as e:
            st.error(f"Failed to log expense: {e}")

    st.markdown("---")
    st.subheader("Your Expenses")
    df = expenses_df(username)
    if df.empty:
        st.info("No expenses yet. Add one above to see analytics.")
    else:
        st.dataframe(df)

        # Export CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download expenses CSV", data=csv, file_name=f"{username}_expenses.csv", mime="text/csv")

        # Quick stats
        st.subheader("Analytics")
        month_start = pd.Timestamp.today().replace(day=1).date()
        total_month = total_spent_month(username, month_start)
        users = read_users()
        goal = float(users.get(username, {}).get("goal", 0.0))

        col1, col2 = st.columns(2)
        col1.metric("Total spent this month", f"${total_month:.2f}")
        col2.metric("Saving goal", f"${goal:.2f}")

        if goal > 0:
            if total_month <= goal:
                st.success("🎉 You are within your goal!")
            else:
                st.warning("⚠ You exceeded your monthly goal.")

        # Graphs
        if st.button("Show Graphs"):
            totals = totals_by_category(username, since_date=month_start)
            if totals:
                cats = list(totals.keys())
                vals = [totals[k] for k in cats]

                col1, col2 = st.columns(2)

                with col1:
                    fig, ax = plt.subplots(figsize=(5,3))
                    ax.bar(cats, vals)
                    ax.set_ylabel("Amount")
                    ax.set_title("Spending by Category (this month)")
                    plt.xticks(rotation=30)
                    st.pyplot(fig)

                with col2:
                    fig2, ax2 = plt.subplots(figsize=(4,4))
                    ax2.pie(vals, labels=cats, autopct="%1.1f%%", startangle=90)
                    ax2.set_title("Spending Distribution")
                    st.pyplot(fig2)
            else:
                st.info("No category totals for this month yet.")

# -------------------------
# AI Tip UI
# -------------------------
def tip_ui():
    st.header("AI Money-Saving Tip")
    st.write("Hugging Face model suggests quick, practical tips. Uses caching + fallback.")
    if st.button("Get Today's Tip"):
        tip = generate_tip()
        st.info(tip)

# -------------------------
# Feedback UI
# -------------------------
def feedback_ui(username):
    st.header("Give Feedback")
    st.write("Tell us what you liked, what to improve, or report bugs. Your feedback helps us improve!")
    with st.form("feedback_form", clear_on_submit=True):
        rating = st.slider("Rating (1 = worst, 5 = best)", min_value=1, max_value=5, value=5)
        feedback_text = st.text_area("Your feedback", placeholder="I liked the AI tips, but wish for dark mode...")
        submitted = st.form_submit_button("Submit Feedback")
        if submitted:
            if not feedback_text.strip():
                st.warning("Please enter some feedback text before submitting.")
            else:
                try:
                    write_feedback(username, feedback_text.strip(), rating)
                    st.success("Thanks for your feedback! ❤️")
                except Exception as e:
                    st.error(f"Failed to save feedback: {e}")

# -------------------------
# Admin Feedback Viewer
# -------------------------
def admin_feedback_view():
    st.header("Admin: View Feedback")
    rows = read_feedback()
    if not rows:
        st.info("No feedback submitted yet.")
        return
    df = pd.DataFrame(rows)
    # convert rating to int
    if 'rating' in df.columns:
        df['rating'] = df['rating'].astype(int)
    st.dataframe(df.sort_values('timestamp', ascending=False))

    # Basic stats
    st.subheader("Feedback Summary")
    avg_rating = df['rating'].mean() if 'rating' in df.columns else None
    count = len(df)
    col1, col2 = st.columns(2)
    col1.metric("Total feedback entries", count)
    if avg_rating is not None:
        col2.metric("Average rating", f"{avg_rating:.2f}")

    # Export feedback CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download feedback CSV", data=csv, file_name="feedback.csv", mime="text/csv")

# -------------------------
# Main
# -------------------------
def main():
    if "user" not in st.session_state:
        login_register_ui()
    else:
        username = st.session_state["user"]
        role = get_user_role(username)
        st.sidebar.success(f"Logged in as {username} ({role})")
        menu = ["Home", "Log Expense", "AI Tip", "Feedback", "Logout"]
        # Admin gets extra option
        if role == "admin":
            menu.insert(4, "Admin: Feedback View")

        choice = st.sidebar.radio("Navigation", menu)

        if choice == "Home":
            st.title("Spendwise Dashboard")
            st.write("Welcome! Use the sidebar to navigate.")
            # quick snapshot
            df = expenses_df(username)
            if not df.empty:
                recent = df.sort_values(by='date', ascending=False).head(5)
                st.subheader("Recent expenses")
                st.table(recent)
            else:
                st.info("No expenses yet. Log one from 'Log Expense'.")

        elif choice == "Log Expense":
            expense_ui(username)
        elif choice == "AI Tip":
            tip_ui()
        elif choice == "Feedback":
            feedback_ui(username)
        elif choice == "Logout":
            st.session_state.pop("user", None)
            st.info("Logged out successfully.")
        elif choice == "Admin: Feedback View" and role == "admin":
            admin_feedback_view()
        else:
            st.info("Select an option from the sidebar.")

if __name__ == "__main__":
    main()