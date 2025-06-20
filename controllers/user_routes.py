from app import app
from flask import render_template,request,redirect, url_for, flash, session
from controllers.rbac import  adminlogin_required
from models import db, User
from datetime import datetime


@app.route('/user_dashboard')
def user_dashboard():
    if 'id' not in session or session.get('role') != 'user':
        flash('Access denied. Please login as a user.', 'danger')
        return redirect(url_for('login'))

    user_id = session.get('id')
    user = User.query.get(user_id)

    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    # You can also fetch user-specific question papers, etc., here
    return render_template('user_templates/user_dashboard.html', user=user, current_year=datetime.now().year)
