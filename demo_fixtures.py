# demo_fixtures.py
import datetime
from utils.data_utils import write_user, log_expense, write_feedback

def seed_demo():
    # Create demo user
    write_user({
        "username": "demo",
        "password": "demo123",
        "purpose": "Save for laptop",
        "goal": 500,
        "role": "user"
    })
    # Create an admin user for feedback viewing
    write_user({
        "username": "admin",
        "password": "admin123",
        "purpose": "Admin user",
        "goal": 0,
        "role": "admin"
    })

    today = datetime.date.today()
    # sample expenses for demo
    log_expense("demo", str(today), "Food", 12.50, "Lunch")
    log_expense("demo", str(today), "Transport", 5.00, "Bus fare")
    log_expense("demo", str(today - datetime.timedelta(days=1)), "Entertainment", 20.00, "Movie night")
    log_expense("demo", str(today - datetime.timedelta(days=2)), "Groceries", 35.00, "Weekly shopping")

    # sample feedback
    write_feedback("demo", "Love the AI tips feature — very helpful!", 5)
    write_feedback("demo", "Would like dark mode and export JSON option.", 4)

    print("Demo user: demo / demo123")
    print("Admin user: admin / admin123")
    print("Seeded sample expenses & feedback.")

if __name__ == "__main__":
    seed_demo()