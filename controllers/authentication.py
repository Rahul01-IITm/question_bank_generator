from app import app
from models import User, db
from controllers.rbac import userlogin_required , adminlogin_required
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# Home route
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', current_year=datetime.now().year)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'id' in session and 'role' in session:
        flash('You are already logged in.', 'info')
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session['role'] == 'user':
            return redirect(url_for('user_dashboard'))
        else:
            return redirect(url_for('index'))  # Default fallback

    if request.method == 'POST':
        username_or_email = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and user.check_password(password):
            session['id'] = user.id
            session['role'] = 'admin' if user.is_admin else 'user'

            flash(f"Welcome back, {user.username}!", 'success')

            # Role-based redirection with default fallback
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            elif not user.is_admin:
                return redirect(url_for('user_dashboard'))
            else:
                return redirect(url_for('index'))  # Fallback in case role is undefined

        flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')




# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get("id"):
        flash('You are already logged in.', 'info')
        return redirect(url_for('admin_dashboard' if session['role'] == 'admin' else 'user_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        pin_code = request.form.get('pin_code')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('Username, Email, and Password are required.')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return render_template('register.html')

        if pin_code and User.query.filter_by(pin_code=pin_code).first():
            flash('Pin code already in use.')
            return render_template('register.html')

        new_user = User(
            username=username,
            email=email,
            full_name=full_name or None,
            pin_code=pin_code or None,
            is_admin=False
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {e}', 'danger')
            return render_template('register.html')

    return render_template('register.html')


# # Logout route
# @app.route('/logout', methods=["POST"])
# def logout():
#     session.pop("id", None)
#     session.pop("role", None)
#     flash('Logged out successfully.', 'info')
#     return redirect(url_for("login"))
