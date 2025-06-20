from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# User table
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)         # New
    full_name = db.Column(db.String(100))                                   # New
    pin_code = db.Column(db.String(10))                                     # New
    password = db.Column(db.String(100), nullable=False)

    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    question_papers = db.relationship('QuestionPaper', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)



# Subject table
class Subject(db.Model):
    __tablename__ = 'subject'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    question_banks = db.relationship('QuestionBank', backref='subject', lazy=True)
    question_papers = db.relationship('QuestionPaper', backref='subject', lazy=True)


# Question Bank table
class QuestionBank(db.Model):
    __tablename__ = 'question_bank'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    
    questions = db.relationship('Question', backref='question_bank', lazy=True)


# Question table
class Question(db.Model):
    __tablename__ = 'question'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)  # 'easy', 'medium', 'hard'
    type = db.Column(db.String)  # MCQ, Descriptive, etc.
    correct_answer = db.Column(db.String)
    
    question_bank_id = db.Column(db.Integer, db.ForeignKey('question_bank.id'), nullable=False)


# Question Paper table
class QuestionPaper(db.Model):
    __tablename__ = 'question_paper'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)
    generation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    
    questions = db.relationship('QuestionPaperQuestion', backref='question_paper', lazy=True)


# Junction table: Question Paper <-> Question
class QuestionPaperQuestion(db.Model):
    __tablename__ = 'question_paper_question'
    
    id = db.Column(db.Integer, primary_key=True)
    question_paper_id = db.Column(db.Integer, db.ForeignKey('question_paper.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    
    question = db.relationship('Question')


# Setup function to initialize the database and create default admin
def setup_database(app_instance, db_instance):
    with app_instance.app_context():
        db_instance.create_all()
        print("Database tables created or verified.")

        # Check if admin already exists
        admin_user = User.query.filter_by(username="admin", is_admin=True).first()
        if not admin_user:
            predefined_admin = User(
                username="admin",
                email="admin@example.com",
                full_name="Admin User",
                pin_code="000000",
                is_admin=True
            )
            predefined_admin.set_password("admin")  # Secure password
            db_instance.session.add(predefined_admin)
            try:
                db_instance.session.commit()
                print("Admin user created successfully.")
            except Exception as e:
                db_instance.session.rollback()
                print(f"Failed to create admin user: {e}")
        else:
            print("Admin user already exists.")
