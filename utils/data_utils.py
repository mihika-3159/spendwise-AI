import csv
import os
USERS_CSV = "users.csv"

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