from app import app
from flask import render_template,request,redirect, url_for, flash, session
from controllers.rbac import  adminlogin_required
from models import db
from datetime import datetime


@app.route("/admin_dashboard")
@adminlogin_required
def admin_dashboard():
    return render_template('admin_templates/admin_dashboard.html')