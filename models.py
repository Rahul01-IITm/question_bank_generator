from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# USER Table
class User(db.Model):
    _tablename_ = 'user'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)

    # Relationships
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)
    auth_sessions = db.relationship('Authentication', backref='user', lazy=True)
    question_papers = db.relationship('QuestionPaper', backref='user', lazy=True)

# ADMIN inherits from USER
class Admin(db.Model):
    _tablename_ = 'admin'
    
    admin_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)

class Authentication(db.Model):
    _tablename_ = 'authentication'
    
    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String)

# FEEDBACK Table
class Feedback(db.Model):
    _tablename_ = 'feedback'
    
    feedback_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    subject = db.Column(db.String)
    message = db.Column(db.String, nullable=False)
    submitted_at = db.Column(db.Date, default=datetime.utcnow)

# QUESTION_BANK Table
class QuestionBank(db.Model):
    _tablename_ = 'question_bank'
    
    bank_id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    # Many-to-many with Question
    questions = db.relationship('Question', secondary='bank_question', backref='banks')

# QUESTION Table
class Question(db.Model):
    _tablename_ = 'question'
    
    question_id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    subject = db.Column(db.String, nullable=False)
    topic = db.Column(db.String)
    difficulty = db.Column(db.String)
    type = db.Column(db.String)
    correct_answer = db.Column(db.String)

# QUESTION_PAPER Table
class QuestionPaper(db.Model):
    _tablename_ = 'question_paper'
    
    paper_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    generation_date = db.Column(db.Date, default=datetime.utcnow)
    subject = db.Column(db.String, nullable=False)
    difficulty_level = db.Column(db.String)

    # Many-to-many with Question
    questions = db.relationship('Question', secondary='paper_question', backref='papers')

# BANK_QUESTION (Junction Table)
class BankQuestion(db.Model):
    _tablename_ = 'bank_question'
    
    bank_id = db.Column(db.Integer, db.ForeignKey('question_bank.bank_id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'), primary_key=True)

# PAPER_QUESTION (Junction Table)
class PaperQuestion(db.Model):
    _tablename_ = 'paper_question'
    
    paper_id = db.Column(db.Integer, db.ForeignKey('question_paper.paper_id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'), primary_key=True)