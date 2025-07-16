from app import app
from flask import render_template,request,redirect, url_for, flash, session, make_response,send_file
from controllers.rbac import  userlogin_required
from models import db, User, QuestionPaperQuestion,Question, QuestionBank, QuestionPaper, Subject
from datetime import datetime
import random
from xhtml2pdf import pisa
import io


@app.route('/user_dashboard')
@userlogin_required
def user_dashboard():
    # if 'user_id' not in session or session.get('role') != 'user':
    #     flash('Access denied. Please login as a user.', 'danger')
    #     return redirect(url_for('login'))

    id = session.get('user_id')
    user = User.query.get(id)

    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    # You can also fetch user-specific question papers, etc., here
    return render_template('user_templates/user_dashboard.html', user=user, current_year=datetime.now().year)


@app.route('/generate_question_paper', methods=['GET', 'POST'])
@userlogin_required
def generate_question_paper():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subject_id = request.form.get('subject_id')
        difficulty = request.form.get('difficulty')
        num_2marks = request.form.get('num_2marks', type=int)
        num_8marks = request.form.get('num_8marks', type=int)
        total_marks = request.form.get('total_marks',type=int)

        if not all([title, subject_id, difficulty]) or num_2marks is None or num_8marks is None:
            flash("All fields are required.", "danger")
            return redirect(url_for('generate_question_paper'))

        # Fetch questions by difficulty and marks
        q_2marks = Question.query.join(QuestionBank).filter(
            QuestionBank.subject_id == subject_id,
            Question.difficulty.ilike(difficulty),
            Question.marks == 2
        ).all()

        q_8marks = Question.query.join(QuestionBank).filter(
            QuestionBank.subject_id == subject_id,
            Question.difficulty.ilike(difficulty),
            Question.marks == 8
        ).all()

        if len(q_2marks) < num_2marks or len(q_8marks) < num_8marks:
            flash(f"Not enough questions available: {len(q_2marks)} (2 marks), {len(q_8marks)} (8 marks).", "warning")
            return redirect(url_for('generate_question_paper'))

        # Randomly sample questions
        selected_2marks = random.sample(q_2marks, num_2marks)
        selected_8marks = random.sample(q_8marks, num_8marks)
        selected_questions = selected_2marks + selected_8marks
        random.shuffle(selected_questions)

        # Create the new question paper
        new_paper = QuestionPaper(
            title=title,
            subject_id=subject_id,
            difficulty=difficulty,
            total_marks=total_marks,
            user_id=session.get('user_id')
        )
        db.session.add(new_paper)
        db.session.commit()  

        # Link questions
        for question in selected_questions:
            db.session.add(QuestionPaperQuestion(
                question_paper_id=new_paper.id,
                question_id=question.id
            ))
        db.session.commit()

        # Display result
        paper = QuestionPaper.query.get(new_paper.id)
        linked_questions = Question.query.join(
            QuestionPaperQuestion, Question.id == QuestionPaperQuestion.question_id
        ).filter(
            QuestionPaperQuestion.question_paper_id == paper.id
        ).all()
        user = User.query.get(session.get('user_id'))

        flash("Question Paper generated successfully!", "success")
        return render_template('user_templates/display_generated_paper.html', paper=paper,total_marks=total_marks, questions=linked_questions, user=user)

    # GET method – show form
    subjects = Subject.query.order_by(Subject.name).all()
    user = User.query.get(session.get('user_id'))
    return render_template("user_templates/generate_question_paper.html", subjects=subjects, user=user,current_year=datetime.now().year)




@app.route('/download_question_paper/<int:paper_id>')
@userlogin_required
def download_question_paper(paper_id):
    paper = QuestionPaper.query.get_or_404(paper_id)
    linked_questions = (
        Question.query
        .join(QuestionPaperQuestion, Question.id == QuestionPaperQuestion.question_id)
        .filter(QuestionPaperQuestion.question_paper_id == paper_id)
        .all()
    )

    # Render the HTML template
    html = render_template(
        'user_templates/question_paper_pdf.html', 
        paper=paper, 
        questions=linked_questions
    )

    # Convert HTML to PDF
    pdf_io = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=pdf_io)

    if pisa_status.err:
        flash("Error generating PDF.", "danger")
        return redirect(url_for('display_generated_paper', paper_id=paper_id))

    pdf_io.seek(0)
    return send_file(
        pdf_io, 
        mimetype='application/pdf',
        download_name=f"{paper.title.replace(' ', '_')}.pdf"
    )