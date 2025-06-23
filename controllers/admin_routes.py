from app import app
from flask import render_template,request,redirect, url_for, flash, session
from controllers.rbac import  adminlogin_required
from models import db
from datetime import datetime


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'id' not in session or session.get('role') != 'admin':
        flash('Access denied. Please login as admin.', 'danger')
        return redirect(url_for('login'))

    # Otherwise, allow dashboard rendering
    return render_template('admin_templates/admin_dashboard.html',current_year=datetime.now().year)
