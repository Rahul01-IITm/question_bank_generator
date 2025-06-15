from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'user'

class Feedback(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class Question(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    topic = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)

class QuestionPaper(db.Model):
    paper_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    generation_date = db.Column(db.DateTime, default=datetime.utcnow)
    subject = db.Column(db.String(50), nullable=False)
    difficulty_level = db.Column(db.String(10), nullable=False)

class QuestionBank(db.Model):
    bank_id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)

class Authentication(db.Model):
    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)