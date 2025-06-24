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
        title = request.form.get('title').strip()
        subject_id = request.form.get('subject_id')
        difficulty = request.form.get('difficulty')
        num_questions = int(request.form.get('num_questions'))

        if not all([title, subject_id, difficulty, num_questions]):
            flash("All fields are required.", "danger")
            return redirect(url_for('generate_question_paper'))

        # Fetch all questions from all question banks for this subject with given difficulty
        all_questions = (
            Question.query
            .join(QuestionBank)
            .filter(
                QuestionBank.subject_id == subject_id,
                Question.difficulty.ilike(difficulty)
            )
            .all()
        )

        if len(all_questions) < num_questions:
            flash(f"Only {len(all_questions)} question(s) available for this subject and difficulty. Cannot generate {num_questions}.", "warning")
            return redirect(url_for('generate_question_paper'))

        # Randomly sample questions
        selected_questions = random.sample(all_questions, num_questions)

        # Create new question paper
        new_paper = QuestionPaper(
            title=title,
            subject_id=subject_id,
            difficulty=difficulty,
            user_id=session.get('user_id')
        )
        db.session.add(new_paper)
        db.session.commit()  # Commit so new_paper gets an ID

        # Link questions
        for question in selected_questions:
            qpq = QuestionPaperQuestion(
                question_paper_id=new_paper.id,
                question_id=question.id
            )
            db.session.add(qpq)

        db.session.commit()

        # Fetch full data and render display page directly
        paper = QuestionPaper.query.get(new_paper.id)
        linked_questions = (
            Question.query
            .join(QuestionPaperQuestion, Question.id == QuestionPaperQuestion.question_id)
            .filter(QuestionPaperQuestion.question_paper_id == paper.id)
            .all()
        )
        user = User.query.get(session.get('user_id'))
        flash("Question Paper generated successfully!", "success")
        return render_template('user_templates/display_generated_paper.html', paper=paper, questions=linked_questions,user=user)

    # GET method – show form
    subjects = Subject.query.order_by(Subject.name).all()
    user = User.query.get(session.get('user_id'))
    return render_template("user_templates/generate_question_paper.html", subjects=subjects, user=user)



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