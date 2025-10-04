# utils/data_utils.py
import csv
import os
import hashlib
import secrets
from typing import Dict, List
import pandas as pd
import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
USERS_CSV = os.path.join(BASE_DIR, "users.csv")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------
# Password hashing helpers
# -------------------------
def _hash_password(password: str, salt: str = None) -> Dict[str,str]:
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return {"salt": salt, "hash": hashed}

def _verify_password(password: str, salt: str, hashed: str) -> bool:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest() == hashed

# -------------------------
# Users (with role)
# -------------------------
def read_users() -> Dict[str, Dict]:
    users = {}
    if not os.path.exists(USERS_CSV):
        return users
    try:
        with open(USERS_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # fields: username, password_hash, salt, purpose, goal, role
                users[row['username']] = {
                    'username': row['username'],
                    'password_hash': row.get('password_hash'),
                    'salt': row.get('salt'),
                    'purpose': row.get('purpose',''),
                    'goal': row.get('goal','0.0'),
                    'role': row.get('role','user')
                }
    except Exception as e:
        print("Error reading users.csv:", e)
    return users

def write_user(user: Dict):
    users = read_users()
    username = user['username']
    # Hash raw password if provided
    if 'password' in user and user['password']:
        ph = _hash_password(user['password'])
        password_hash = ph['hash']
        salt = ph['salt']
    else:
        password_hash = user.get('password_hash','')
        salt = user.get('salt','')
    role = user.get('role', 'user')
    users[username] = {
        'username': username,
        'password_hash': password_hash,
        'salt': salt,
        'purpose': user.get('purpose',''),
        'goal': str(user.get('goal','0.0')),
        'role': role
    }
    fieldnames = ['username','password_hash','salt','purpose','goal','role']
    try:
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for u in users.values():
                writer.writerow(u)
    except Exception as e:
        print("Error writing users.csv:", e)
        raise

def verify_user_credentials(username: str, password: str) -> bool:
    users = read_users()
    if username not in users:
        return False
    user = users[username]
    salt = user.get('salt')
    phash = user.get('password_hash')
    if not salt or not phash:
        return False
    return _verify_password(password, salt, phash)

def get_user_role(username: str) -> str:
    users = read_users()
    if username not in users:
        return 'user'
    return users[username].get('role','user')

# -------------------------
# Expenses
# -------------------------
def _expense_path(username: str) -> str:
    return os.path.join(DATA_DIR, f"{username}_expenses.csv")

def log_expense(username: str, date: str, category: str, amount: float, description: str):
    path = _expense_path(username)
    file_exists = os.path.exists(path)
    fieldnames = ['date','category','amount','description']
    try:
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
    except Exception as e:
        print(f"Error logging expense for {username}: {e}")
        raise

def read_expenses(username: str) -> List[Dict]:
    path = _expense_path(username)
    if not os.path.exists(path):
        return []
    rows = []
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except Exception as e:
        print(f"Error reading expenses for {username}: {e}")
    return rows

# -------------------------
# Analytics helpers
# -------------------------
def expenses_df(username: str) -> pd.DataFrame:
    rows = read_expenses(username)
    if not rows:
        return pd.DataFrame(columns=['date','category','amount','description'])
    df = pd.DataFrame(rows)
    df['amount'] = df['amount'].astype(float)
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df

def totals_by_category(username: str, since_date=None) -> Dict[str, float]:
    df = expenses_df(username)
    if since_date is not None and not df.empty:
        df = df[df['date'] >= since_date]
    if df.empty:
        return {}
    totals = df.groupby('category')['amount'].sum().to_dict()
    return totals

def total_spent_month(username: str, month_start_date) -> float:
    df = expenses_df(username)
    if df.empty:
        return 0.0
    df = df[df['date'] >= month_start_date]
    return float(df['amount'].sum())

# -------------------------
# Feedback (global file)
# -------------------------
FEEDBACK_CSV = os.path.join(DATA_DIR, "feedback.csv")

def write_feedback(username: str, feedback_text: str, rating: int):
    """
    Append a feedback row: timestamp, username, rating, feedback_text
    """
    fieldnames = ['timestamp','username','rating','feedback']
    file_exists = os.path.exists(FEEDBACK_CSV)
    try:
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
    except Exception as e:
        print("Error writing feedback:", e)
        raise

def read_feedback() -> List[Dict]:
    """
    Return list of feedback dictionaries (timestamp, username, rating, feedback)
    """
    if not os.path.exists(FEEDBACK_CSV):
        return []
    rows = []
    try:
        with open(FEEDBACK_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except Exception as e:
        print("Error reading feedback:", e)
    return rows