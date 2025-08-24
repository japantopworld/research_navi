# models/user_model.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    furigana = db.Column(db.String(100))
    birthdate = db.Column(db.String(20))
    age = db.Column(db.Integer)
    tel = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(100))
    department = db.Column(db.String(100))
    ref_no = db.Column(db.String(50))
    login_id = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
