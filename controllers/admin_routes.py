from app import app
from flask import render_template,request,redirect, url_for, flash, session
from controllers.rbac import  adminlogin_required
from models import db, Subject, QuestionBank
from datetime import datetime


@app.route('/admin_dashboard')
def admin_dashboard():
    # Session-based admin access check
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Please login as admin.', 'danger')
        return redirect(url_for('login'))

    
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
        subject_name = request.form.get('name')
        if subject_name:
            existing = Subject.query.filter_by(name=subject_name.strip()).first()
            if existing:
                flash('Subject already exists.', 'warning')
            else:
                new_subject = Subject(name=subject_name.strip())
                db.session.add(new_subject)
                db.session.commit()
                flash('Subject added successfully.', 'success')
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Subject name cannot be empty.', 'danger')

    return render_template('admin_templates/add_subject.html')
