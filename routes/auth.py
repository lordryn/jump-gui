# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, make_response
from services.user_service import UserService

auth_bp = Blueprint('auth', __name__)
user_service = UserService()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if user_service.verify_credentials(username, password):
            session.permanent = True
            session['username'] = username
            resp = make_response(redirect(url_for('device.index')))
            resp.set_cookie('username', username, max_age=60 * 60 * 24 * 7)
            return resp
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    resp = make_response(redirect(url_for('auth.login')))
    resp.set_cookie('username', '', expires=0)
    return resp
