
import csv
import os
import datetime
import streamlit as st
from utils.data_utils import read_users, write_user
from utils.tips import generate_tip
from utils import CATEGORIES
from utils import ai_helper

# --- LOGIN & REGISTRATION SYSTEM ---
def login_register_ui():
    # NOTE: Passwords are stored in plaintext in users.csv.
    # For a real application, use password hashing (e.g., bcrypt) before saving.
    st.title("SpendWise Login / Register")
    users = read_users()
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if st.session_state.page == 'login':
        st.header("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            try:
                if username in users and users[username]['password'] == password:
                    st.session_state.current_user = users[username]
                    st.session_state.page = 'main'
                    st.success("Login successful!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password.")
            except Exception:
                st.error("An error occurred during login. Please try again later.")
        st.write("Don't have an account?")
        if st.button("Register"):
            st.session_state.page = 'register'
            st.experimental_rerun()
    elif st.session_state.page == 'register':
        st.header("Register New Account")
        reg_username = st.text_input("Choose a username", key="reg_username")
        reg_password = st.text_input("Choose a password", type="password", key="reg_password")
        reg_email = st.text_input("Email address", key="reg_email")
        reg_goal = st.text_input("Monthly savings goal ($)", key="reg_goal")
        if st.button("Create Account"):
            try:
                if not reg_username or not reg_password or not reg_email or not reg_goal:
                    st.error("All fields are required.")
                elif reg_username in users:
                    st.error("Username already exists. Please choose another.")
                else:
                    try:
                        float(reg_goal)
                    except ValueError:
                        st.error("Goal must be a number.")
                        return
                    user = {
                        'username': reg_username,
                        'password': reg_password,
                        'purpose': reg_email,
                        'goal': reg_goal
                    }
                    write_user(user)
                    st.success("Account created! Please log in.")
                    st.session_state.page = 'login'
                    st.experimental_rerun()
            except Exception:
                st.error("An error occurred during registration. Please try again later.")
        st.write("Already have an account?")
        if st.button("Back to Login"):
            st.session_state.page = 'login'
            st.experimental_rerun()


USERS_CSV = "users.csv"
def get_expenses(username):
    expenses = []
    expenses_file = f"data/{username}_expenses.csv"
    if os.path.exists(expenses_file):
        try:
            with open(expenses_file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    expenses.append(row)
        except Exception as e:
            st.error("Could not read expenses file. Please try again later.")
            print(f"Error reading {expenses_file}: {e}")
    return expenses


def log_expense(username, date, category, amount, description):
    expenses_file = f"{username}_expenses.csv"
    file_exists = os.path.exists(expenses_file)
    with open(expenses_file, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['date', 'category', 'amount', 'description']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'date': date,
            'category': category,
            'amount': amount,
            'description': description
        })

# Move log_feedback to top-level
def log_feedback(username, date, tip_text, feedback):
    feedback_file = "feedback.csv"
    file_exists = os.path.exists(feedback_file)
    with open(feedback_file, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['username', 'date', 'tip_text', 'feedback']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'username': username,
            'date': date,
            'tip_text': tip_text,
            'feedback': feedback
        })


# --- MAIN APP ENTRYPOINT ---
def main():
    if 'current_user' not in st.session_state or st.session_state.current_user is None:
        login_register_ui()
    else:
        # --- Main UI (existing code, now as a function) ---
        user = st.session_state.current_user
        st.header(f"Welcome, {user['username']}! Goal: ${user['goal']}/month")
        if st.button("Logout"):
            st.session_state.current_user = None
            st.session_state.page = "login"
            st.experimental_rerun()

        st.subheader("Log Expense")
        with st.form("log_expense_form"):
            category = st.selectbox("Category", CATEGORIES)
            amount = st.text_input("Amount")
            description = st.text_input("Description")
            submitted = st.form_submit_button("Submit")
            if submitted:
                try:
                    amount_val = float(amount)
                    if amount_val <= 0:
                        raise ValueError
                    date = datetime.date.today().isoformat()
                    log_expense(user['username'], date, category, amount_val, description)
                    st.success("Expense logged!")
                except ValueError:
                    st.error("Invalid amount")
                except Exception:
                    st.error("Could not log expense. Please try again later.")

        st.subheader("Summaries")
        if st.button("Weekly Summary"):
            try:
                expenses = get_expenses(user['username'])
                now = datetime.date.today()
                week_ago = now - datetime.timedelta(days=7)
                summary = {cat: 0.0 for cat in CATEGORIES}
                for e in expenses:
                    date = datetime.date.fromisoformat(e['date'])
                    if week_ago <= date <= now:
                        summary[e['category']] += float(e['amount'])
                st.write("### Weekly Summary")
                for cat, amt in summary.items():
                    st.write(f"{cat}: ${amt:.2f}")
            except Exception:
                st.error("Could not generate weekly summary. Please try again later.")

        if st.button("Monthly Summary"):
            try:
                expenses = get_expenses(user['username'])
                now = datetime.date.today()
                month_start = now.replace(day=1)
                total_spent = 0.0
                for e in expenses:
                    date = datetime.date.fromisoformat(e['date'])
                    if date >= month_start:
                        total_spent += float(e['amount'])
                goal = float(user['goal'])
                savings = goal - total_spent
                if savings > 0:
                    status = f"You have saved ${savings:.2f} this month. Great job!"
                    new_goal = goal + 0.05 * goal
                    suggestion = f"Your goal will increase to ${new_goal:.2f} next month."
                elif savings == 0:
                    status = "You have exactly met your savings goal."
                    new_goal = goal
                    suggestion = "Keep up the consistency!"
                else:
                    status = f"You fell short of your goal by ${-savings:.2f}."
                    new_goal = max(goal - 0.05 * goal, 0)
                    suggestion = f"Your goal will decrease to ${new_goal:.2f} next month."
                # Update goal for next month
                user['goal'] = f"{new_goal:.2f}"
                write_user(user)
                st.session_state.current_user = user
                st.write(f"### Monthly Summary\nTotal Spent: ${total_spent:.2f}\n{status}\n{suggestion}")
            except Exception:
                st.error("Could not generate monthly summary. Please try again later.")

        if st.button("Spending Suggestions"):
            try:
                expenses = get_expenses(user['username'])
                now = datetime.date.today()
                month_start = now.replace(day=1)
                category_totals = {cat: 0.0 for cat in CATEGORIES}
                for e in expenses:
                    date = datetime.date.fromisoformat(e['date'])
                    if date >= month_start:
                        category_totals[e['category']] += float(e['amount'])
                most_spent = max(category_totals, key=category_totals.get)
                st.write("### Spending Suggestions")
                if category_totals[most_spent] > 0:
                    st.write(f"You are spending the most on {most_spent} (${category_totals[most_spent]:.2f}). Consider reducing this category.")
                else:
                    st.write("No expenses logged this month yet.")
                for cat, amt in category_totals.items():
                    if amt == 0:
                        st.write(f"Try to log your {cat} expenses for better tracking.")
            except Exception:
                st.error("Could not generate suggestions. Please try again later.")

        st.subheader("💡 Daily Money Tip")
        try:
            tip = generate_tip()
            st.info(tip)
        except Exception:
            st.error("Could not generate daily tip. Please try again later.")

        st.subheader("🤖 AI Tip of the Day")
        try:
            with st.spinner("Fetching AI tip..."):
                ai_tip = ai_helper.get_ai_suggestion()
            st.info(ai_tip)
            col1, col2 = st.columns(2)
            now = datetime.date.today().isoformat()
            if col1.button("👍", key="ai_tip_upvote"):
                log_feedback(user['username'], now, ai_tip, "up")
                st.success("Thanks for your feedback!")
            if col2.button("👎", key="ai_tip_downvote"):
                log_feedback(user['username'], now, ai_tip, "down")
                st.success("Thanks for your feedback!")
        except Exception:
            st.error("Could not fetch AI tip. Please try again later.")

# --- Run the app ---
if __name__ == "__main__":
    main()