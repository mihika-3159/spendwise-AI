import csv
import os
import datetime
import streamlit as st

USERS_CSV = "users.csv"
CATEGORIES = ["Food", "Transport", "Entertainment", "Utilities", "Other"]

def read_users():
    users = {}
    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users[row['username']] = row
    return users

def write_user(user):
    users = read_users()
    users[user['username']] = user
    with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['username', 'password', 'purpose', 'goal']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for u in users.values():
            writer.writerow(u)

def get_expenses(username):
    expenses = []
    expenses_file = f"{username}_expenses.csv"
    if os.path.exists(expenses_file):
        with open(expenses_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                expenses.append(row)
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

def streamlit_main():
    st.set_page_config(page_title="SpendWise - Financial Coach", layout="centered")
    st.title("SpendWise - Financial Coach")

    # Session state for user
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

    def login_ui():
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            users = read_users()
            if username in users and users[username]['password'] == password:
                st.session_state.current_user = users[username]
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")
        if st.button("Go to Register"):
            st.session_state.page = "register"
            st.experimental_rerun()

    def register_ui():
        st.subheader("Register")
        username = st.text_input("Username", key="reg_username")
        password = st.text_input("Password", type="password", key="reg_password")
        purpose = st.text_input("Purpose of using this app", key="reg_purpose")
        goal = st.text_input("Goal savings per month", key="reg_goal")
        if st.button("Register"):
            users = read_users()
            if username in users:
                st.error("Username already exists")
                return
            if not username or not password or not purpose or not goal.isdigit():
                st.error("Please fill all fields correctly")
                return
            user = {
                'username': username,
                'password': password,
                'purpose': purpose,
                'goal': goal
            }
            write_user(user)
            st.success("Registration successful! Please login.")
            st.session_state.page = "login"
            st.experimental_rerun()
        if st.button("Back to Login"):
            st.session_state.page = "login"
            st.experimental_rerun()

    def main_ui():
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

        st.subheader("Summaries")
        if st.button("Weekly Summary"):
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

        if st.button("Monthly Summary"):
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

        if st.button("Spending Suggestions"):
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

    # Page routing
    if 'page' not in st.session_state:
        st.session_state.page = "login"
    if st.session_state.current_user:
        main_ui()
    elif st.session_state.page == "register":
        register_ui()
    else:
        login_ui()

if __name__ == "__main__":
    streamlit_main()