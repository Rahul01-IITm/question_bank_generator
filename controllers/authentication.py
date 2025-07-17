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
    
    if request.method == 'POST':
        username_or_email = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember_me') == 'on'

        # Try finding user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and user.check_password(password):
            # Set session
            session['user_id'] = user.id
            session['role'] = 'admin' if user.is_admin else 'user'
            session.permanent = remember

            flash(f'Logged in successfully as {session["role"].capitalize()}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            # Redirect based on role
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))

        flash('Invalid username or password. Please try again.', 'danger')

    # For GET request or failed POST
    return render_template('login.html',current_year=datetime.now().year)





# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 1. Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        pin_code = request.form.get('pin_code')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # 2. Server-side validation
        if not all([username, email, full_name, pin_code, password, confirm_password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        # 3. Check for existing user
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email address is already registered.', 'danger')
            return redirect(url_for('register'))

        # 4. Create new user instance
        # Note: 'is_admin' defaults to False as per your model definition
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            pin_code=pin_code
        )
        
        # 5. Set the hashed password
        new_user.set_password(password)

        # 6. Add to database
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration: {e}', 'danger')
            return redirect(url_for('register'))

    # If method is GET, just render the registration form
    return render_template('register.html',current_year=datetime.now().year)


@app.route('/logout', methods=["POST", "GET"])
def logout():
    session.pop("user_id", None)
    session.pop("role", None)
    return redirect(url_for("login"))

