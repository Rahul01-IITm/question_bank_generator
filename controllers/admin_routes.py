from app import app
from flask import render_template,request,redirect, url_for, flash, session
from controllers.rbac import  adminlogin_required
from models import db, Subject, QuestionBank, Question, User 
from datetime import datetime
from sqlalchemy import func


@app.route('/admin_dashboard')
@adminlogin_required
def admin_dashboard():
    # Session-based admin access check
    # if 'user_id' not in session or session.get('role') != 'admin':
    #     flash('Access denied. Please login as admin.', 'danger')
    #     return redirect(url_for('login'))

    
    subjects = Subject.query.all()
    question_banks = QuestionBank.query.all()

    return render_template(
        'admin_templates/admin_dashboard.html',
        question_banks=question_banks,
        subjects=subjects,
        current_year=datetime.now().year
    )


@app.route('/add_subject', methods=['GET', 'POST'])
@adminlogin_required
def add_subject():
    if request.method == 'POST':
        subject_name = request.form.get('name', '').strip()

        if not subject_name:
            flash('Subject name cannot be empty.', 'danger')
            return redirect(url_for('add_subject'))

        # Case-insensitive subject check
        existing = Subject.query.filter(func.lower(Subject.name) == subject_name.lower()).first()

        if existing:
            flash('Subject already exists.', 'warning')
        else:
            new_subject = Subject(name=subject_name)
            db.session.add(new_subject)
            db.session.commit()
            flash('Subject added successfully.', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('admin_templates/add_subject.html')



@app.route('/add_questionbank', methods=['GET', 'POST'])
@adminlogin_required
def add_questionbank():
    if request.method == 'POST':
        subject_name_input = request.form.get('subject_name', '').strip()
        bank_name_input = request.form.get('question_bank_name', '').strip()

        if not subject_name_input or not bank_name_input:
            flash('Both fields are required.', 'danger')
            return redirect(url_for('add_questionbank'))

        # Normalize inputs to lowercase for comparison
        subject = Subject.query.filter(func.lower(Subject.name) == subject_name_input.lower()).first()

        if not subject:
            flash('Subject does not exist. Please add the subject first.', 'warning')
            return redirect(url_for('add_subject'))

        # Prevent duplicate bank names (case-insensitive) under the same subject
        existing_bank = QuestionBank.query.filter(
            func.lower(QuestionBank.name) == bank_name_input.lower(),
            QuestionBank.subject_id == subject.id
        ).first()

        if existing_bank:
            flash('A question bank with this name already exists for the subject.', 'warning')
            return redirect(url_for('add_questionbank'))

        # Create and save new question bank
        new_bank = QuestionBank(name=bank_name_input, subject_id=subject.id)
        db.session.add(new_bank)
        db.session.commit()

        flash('Question bank added successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_templates/add_questionbank.html')



@app.route('/add_questions', methods=['GET', 'POST'])
@adminlogin_required
def add_questions():
    

    if request.method == 'POST':
        question_bank_id = request.form.get('question_bank_id')
        text = request.form.get('text', '').strip()
        difficulty = request.form.get('difficulty', '').strip().lower()
        q_type = request.form.get('type', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip()

        # Validate question bank exists
        bank = QuestionBank.query.get(question_bank_id)
        if not bank:
            flash("Selected Question Bank does not exist.", "danger")
            return redirect(url_for('add_questions'))

        if not text or not difficulty or not q_type or not correct_answer:
            flash("All fields are required.", "warning")
            return redirect(url_for('add_questions'))

        # Create and add the question
        question = Question(
            text=text,
            difficulty=difficulty,
            type=q_type,
            correct_answer=correct_answer,
            question_bank_id=question_bank_id
        )
        db.session.add(question)
        db.session.commit()
        flash("Question added successfully.", "success")
        return redirect(url_for('admin_dashboard'))

    # GET request: show form
    question_banks = QuestionBank.query.all()
    if not question_banks:
        flash("No Question Banks found. Please add a Question Bank first.", "warning")
        return redirect(url_for('add_questionbank'))  # Optional redirect

    return render_template(
        'admin_templates/add_questions.html',
        question_banks=question_banks
    )


@app.route('/user_information')
@adminlogin_required
def user_information():
    users = User.query.all()
    return render_template('admin_templates/user_information.html', users=users)

