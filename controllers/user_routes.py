from app import app
from flask import render_template,request,redirect, url_for, flash, session,send_file
from controllers.rbac import  userlogin_required
from models import db, User, QuestionPaperQuestion,Question, QuestionBank, QuestionPaper, Subject
from datetime import datetime 
from zoneinfo import ZoneInfo
import random
from xhtml2pdf import pisa
import io


@app.route('/user_dashboard')
@userlogin_required
def user_dashboard():
    
    id = session.get('user_id')
    user = User.query.get(id)

    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    # You can also fetch user-specific question papers, etc., here
    return render_template('user_templates/user_dashboard.html', user=user, current_year=datetime.now().year)


@app.route('/view_papers', methods=['GET'])
@userlogin_required
def view_question_papers():
    query = request.args.get('query', '').strip()
    id = session.get('user_id')
    user = User.query.get(id)
    
    
    if query:
        results = QuestionPaper.query.filter(
            QuestionPaper.title.ilike(f"%{query}%")
        ).all()
    else:
        results = QuestionPaper.query.filter_by(user_id=user.id).order_by(QuestionPaper.id.desc()).all()


    return render_template('user_templates/view_papers.html', user=user,results=results, query=query,current_year=datetime.now().year)



@app.route('/generate_question_paper', methods=['GET', 'POST'])
@userlogin_required
def generate_question_paper():
    if request.method == 'POST':
        form_data = request.form.to_dict()

        title = form_data.get('title')
        subject_id = form_data.get('subject_id')
        difficulty = form_data.get('difficulty')
        semester = form_data.get('semester')
        exam_year = form_data.get('exam_year')
        time_allotted = form_data.get('time_allotted')
        total_marks = int(form_data.get('total_marks') or 0)
        num_2marks = int(form_data.get('num_2marks') or 0)
        num_8marks = int(form_data.get('num_8marks') or 0)

        # Fetch questions from database
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

        errors = []
        if len(q_2marks) < num_2marks:
            errors.append(f"{len(q_2marks)} out of {num_2marks} questions for (2-mark)")
        if len(q_8marks) < num_8marks:
            errors.append(f"{len(q_8marks)} out of {num_8marks} questions for (8-mark)")

        if errors:
            flash(f"Questions available: {' and '.join(errors)}", "danger")
            session['form_data'] = form_data
            return redirect(url_for('generate_question_paper'))


        # Create and save question paper
        new_paper = QuestionPaper(
            title=title,
            subject_id=subject_id,
            difficulty=difficulty,
            total_marks=total_marks,
            semester=semester,
            exam_year=exam_year,
            time_allotted=int(time_allotted) if time_allotted else None,
            user_id=session.get('user_id'),
            generation_date=datetime.now(ZoneInfo("Asia/Kolkata"))
        )
        db.session.add(new_paper)
        db.session.commit()

        # Link selected questions
        for question in random.sample(q_2marks, num_2marks) + random.sample(q_8marks, num_8marks):
            db.session.add(QuestionPaperQuestion(
                question_paper_id=new_paper.id,
                question_id=question.id
            ))
        db.session.commit()

        session['display_semester'] = semester
        session['display_exam_year'] = exam_year
        session['display_time_allotted'] = time_allotted

        return redirect(url_for('display_generated_paper', paper_id=new_paper.id))

    # GET Request
    subjects = Subject.query.order_by(Subject.name).all()
    user = User.query.get(session.get('user_id'))
    form_data = session.pop('form_data', {})
    return render_template("user_templates/generate_question_paper.html", subjects=subjects, user=user, form_data=form_data, current_year=datetime.now().year)




@app.route('/display_generated_paper/<int:paper_id>')
@userlogin_required
def display_generated_paper(paper_id):
    paper = QuestionPaper.query.get_or_404(paper_id)
    user = User.query.get(session.get('user_id'))

    linked_questions = Question.query.join(
        QuestionPaperQuestion, Question.id == QuestionPaperQuestion.question_id
    ).filter(
        QuestionPaperQuestion.question_paper_id == paper.id
    ).all()

    group_a = [q for q in linked_questions if q.marks == 2]
    group_b = [q for q in linked_questions if q.marks == 8]

    
    semester = session.get('display_semester', None)
    exam_year = session.get('display_exam_year', None)
    time_allotted = session.get('display_time_allotted', None)
    total_marks = paper.total_marks

    if time_allotted:
        try:
            time_allotted = int(time_allotted)
        except ValueError:
            time_allotted = None

    flash("Question Paper generated successfully!", "success")
    return render_template(
        'user_templates/display_generated_paper.html',
        paper=paper,
        group_a=group_a,
        group_b=group_b,
        total_marks=total_marks,
        questions=linked_questions,
        user=user,
        semester=semester,
        exam_year=exam_year,
        time_allotted=time_allotted,
        current_year=datetime.now().year
    )






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

    group_a = [q for q in linked_questions if q.marks == 2]
    group_b = [q for q in linked_questions if q.marks == 8]

    html = render_template(
        'user_templates/question_paper_pdf.html',
        paper=paper,
        group_a=group_a,
        group_b=group_b
    )

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

