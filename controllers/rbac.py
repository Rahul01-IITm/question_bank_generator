from functools import wraps
from flask import session, redirect, url_for, flash
from models import User


# Decorator for authentication of users
def userlogin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if "user_id" in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for("login"))

    return inner


# Decorator for authentication of admin
def adminlogin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))

        user = User.query.get(session["user_id"])

        if not user.is_admin:
            flash("You are not authorized to access this page")
            return redirect(url_for("index"))
        return func(*args, **kwargs)

    return inner
