# demo_fixtures.py
import datetime
from utils.data_utils import write_user, log_expense, write_feedback

def seed_demo():
    # demo user (activated)
    write_user({
        "username": "demo",
        "password": "demo123",
        "purpose": "Save for a laptop",
        "goal": 400,
        "role": "user",
        "activated": True,
        "activation_code": "",
        "email": "demo@example.com"
    })

    # admin user (activated)
    write_user({
        "username": "admin",
        "password": "admin123",
        "purpose": "Administrator",
        "goal": 0,
        "role": "admin",
        "activated": True,
        "activation_code": "",
        "email": "admin@example.com"
    })

    # Add some sample expenses + feedback for demo
    today = datetime.date.today()
    log_expense("demo", str(today), "Food", 12.5, "Lunch")
    log_expense("demo", str(today), "Transport", 5.0, "Bus")
    log_expense("demo", str(today - datetime.timedelta(days=1)), "Entertainment", 20.0, "Movie")
    log_expense("demo", str(today - datetime.timedelta(days=3)), "Groceries", 36.0, "Groceries")

    write_feedback("demo", "Love the personalized tips!", 5)
    write_feedback("demo", "Would be nice to have dark mode.", 4)

    print("✅ Seeded demo and admin users successfully.")