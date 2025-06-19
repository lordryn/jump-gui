from flask import Flask, render_template, request, redirect, url_for, session, make_response
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, create_engine, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
Base = declarative_base()

# Database models
class Device(Base):
    __tablename__ = 'device'
    id = Column(Integer, primary_key=True)
    hostname = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    status = Column(String, default='unknown')
    registered = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, default='')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

# SQLite engine setup
engine = create_engine('sqlite:///devices.db', echo=True)
SessionLocal = sessionmaker(bind=engine)
db_session = SessionLocal()

# Create tables if not already present
Base.metadata.create_all(bind=engine)

# Ensure default admin exists
if not db_session.query(User).filter_by(username='admin').first():
    db_session.add(User(username='admin', password='Password123'))
    db_session.commit()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    devices = db_session.query(Device).all()
    return render_template('devices.html', devices=devices)

@app.route('/register', methods=['POST'])
@login_required
def register():
    hostname = request.form['hostname']
    port = request.form['port']
    notes = request.form.get('notes', '')
    new_device = Device(hostname=hostname, port=int(port), notes=notes)
    db_session.add(new_device)
    db_session.commit()
    return redirect(url_for('index'))

@app.route('/ping/<int:device_id>', methods=['POST'])
@login_required
def ping_device(device_id):
    device = db_session.query(Device).get(device_id)
    if device:
        device.status = "Online"
        db_session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:device_id>', methods=['POST'])
@login_required
def delete_device(device_id):
    device = db_session.query(Device).get(device_id)
    if device:
        db_session.delete(device)
        db_session.commit()
    return redirect(url_for('index'))

@app.route('/console/<int:device_id>')
@login_required
def console_device(device_id):
    device = db_session.query(Device).get(device_id)
    return f"Console view for {device.hostname} (Port: {device.port})"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db_session.query(User).filter_by(username=username, password=password).first()
        if user:
            session.permanent = True
            session['username'] = user.username
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('username', user.username, max_age=60*60*24*7)
            return resp
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('username', '', expires=0)
    return resp

if __name__ == '__main__':
    app.run()
