# utils/data_utils.py
import os
import csv
import datetime
from typing import Dict, List, Optional
import bcrypt
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
USERS_CSV = os.path.join(BASE_DIR, "users.csv")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

FEEDBACK_CSV = os.path.join(DATA_DIR, "feedback.csv")

# Ensure users CSV exists with headers
def _ensure_users_csv():
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "username","password_hash","salt","purpose","goal","role","activated","activation_code","email"
            ])
            writer.writeheader()

def read_users() -> Dict[str, Dict]:
    _ensure_users_csv()
    users = {}
    with open(USERS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users[row["username"]] = {
                "username": row["username"],
                "password_hash": row.get("password_hash",""),
                "salt": row.get("salt",""),
                "purpose": row.get("purpose",""),
                "goal": float(row.get("goal","0") or 0),
                "role": row.get("role","user"),
                "activated": row.get("activated","False") == "True",
                "activation_code": row.get("activation_code",""),
                "email": row.get("email","")
            }
    return users

def write_user(user: Dict):
    """
    Accepts either raw 'password' to hash, or precomputed password_hash+salt.
    Stores activated flag and activation_code.
    """
    _ensure_users_csv()
    users = read_users()
    username = user["username"]
    if "password" in user and user["password"]:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(user["password"].encode("utf-8"), salt).decode("utf-8")
        salt_str = salt.decode("utf-8")
    else:
        hashed = user.get("password_hash","")
        salt_str = user.get("salt","")
    users[username] = {
        "username": username,
        "password_hash": hashed,
        "salt": salt_str,
        "purpose": user.get("purpose",""),
        "goal": float(user.get("goal",0.0) or 0.0),
        "role": user.get("role","user"),
        "activated": user.get("activated", False),
        "activation_code": user.get("activation_code",""),
        "email": user.get("email","")
    }
    with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "username","password_hash","salt","purpose","goal","role","activated","activation_code","email"
        ])
        writer.writeheader()
        for u in users.values():
            writer.writerow({
                "username": u["username"],
                "password_hash": u.get("password_hash",""),
                "salt": u.get("salt",""),
                "purpose": u.get("purpose",""),
                "goal": u.get("goal",0.0),
                "role": u.get("role","user"),
                "activated": str(u.get("activated", False)),
                "activation_code": u.get("activation_code",""),
                "email": u.get("email","")
            })

def verify_user_credentials(username: str, password: str) -> bool:
    users = read_users()
    if username not in users:
        return False
    u = users[username]
    if not u.get("activated", False):
        return False
    stored_hash = u.get("password_hash","").encode("utf-8")
    try:
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash)
    except Exception:
        return False

def get_user_role(username: str) -> str:
    return read_users().get(username, {}).get("role", "user")

def is_user_activated(username: str) -> bool:
    return read_users().get(username, {}).get("activated", False)

def set_user_activation(username: str, activated: bool):
    users = read_users()
    if username in users:
        users[username]["activated"] = activated
        users[username]["activation_code"] = ""
        write_user(users[username])

def get_activation_code(username: str) -> str:
    return read_users().get(username, {}).get("activation_code","")

# Expense helpers
def _expense_path(username: str) -> str:
    return os.path.join(DATA_DIR, f"{username}_expenses.csv")

def log_expense(username: str, date: str, category: str, amount: float, description: str):
    path = _expense_path(username)
    file_exists = os.path.exists(path)
    fieldnames = ['date','category','amount','description']
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'date': date,
            'category': category,
            'amount': f"{amount:.2f}",
            'description': description
        })

def read_expenses(username: str) -> List[Dict]:
    path = _expense_path(username)
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows

def expenses_df(username: str):
    rows = read_expenses(username)
    if not rows:
        return pd.DataFrame(columns=['date','category','amount','description'])
    df = pd.DataFrame(rows)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
    return df

def totals_by_category(username: str, since_date=None):
    df = expenses_df(username)
    if since_date is not None and not df.empty:
        df = df[df['date'] >= since_date]
    if df.empty:
        return {}
    return df.groupby('category')['amount'].sum().to_dict()

def total_spent_month(username: str, month_start_date):
    df = expenses_df(username)
    if df.empty:
        return 0.0
    df = df[df['date'] >= month_start_date]
    return float(df['amount'].sum())

# Feedback
def write_feedback(username: str, feedback_text: str, rating: int):
    file_exists = os.path.exists(FEEDBACK_CSV)
    fieldnames = ['timestamp','username','rating','feedback']
    with open(FEEDBACK_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'username': username,
            'rating': int(rating),
            'feedback': feedback_text
        })

def read_feedback() -> List[Dict]:
    if not os.path.exists(FEEDBACK_CSV):
        return []
    rows = []
    with open(FEEDBACK_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            # normalize keys
            if 'timestamp' not in r:
                r['timestamp'] = ''
            if 'rating' in r and r['rating'] != '':
                try:
                    r['rating'] = int(r['rating'])
                except:
                    r['rating'] = None
            else:
                r['rating'] = None
            rows.append(r)
    return rows