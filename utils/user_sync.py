import csv, os
from models.user import User, db

CSV_PATH = "data/users.csv"

def save_user_to_csv(user: User):
    """ユーザーをCSVに保存"""
    file_exists = os.path.isfile(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["username", "password", "email"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(user.to_dict())

def sync_csv_to_db():
    """CSVの内容をDBに反映"""
    if not os.path.isfile(CSV_PATH):
        return
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not User.query.filter_by(username=row["username"]).first():
                user = User(username=row["username"], password=row["password"], email=row.get("email"))
                db.session.add(user)
        db.session.commit()
