from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, create_engine, inspect
from sqlalchemy.orm import declarative_base, sessionmaker

app = Flask(__name__)
Base = declarative_base()

# Database model
class Device(Base):
    __tablename__ = 'device'
    id = Column(Integer, primary_key=True)
    hostname = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    status = Column(String, default='unknown')
    registered = Column(DateTime, default=datetime.utcnow)

# SQLite engine setup
engine = create_engine('sqlite:///devices.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Create tables if not already present
if not inspect(engine).has_table("device"):
    Base.metadata.create_all(bind=engine)

# Homepage shows all devices
@app.route('/')
def index():
    devices = session.query(Device).all()
    return render_template('devices.html', devices=devices)

# Register new device
@app.route('/register', methods=['POST'])
def register():
    hostname = request.form['hostname']
    port = request.form['port']
    new_device = Device(hostname=hostname, port=int(port))
    session.add(new_device)
    session.commit()
    return redirect(url_for('index'))


# Ping a device
@app.route('/ping/<int:device_id>', methods=['POST'])
def ping_device(device_id):
    device = session.query(Device).get(device_id)
    if not device:
        return "Device not found", 404
    device.status = "Online"
    session.commit()
    return redirect(url_for('index'))

# Delete a device
@app.route('/delete/<int:device_id>', methods=['POST'])
def delete_device(device_id):
    device = session.query(Device).get(device_id)
    if not device:
        return "Device not found", 404
    session.delete(device)
    session.commit()
    return redirect(url_for('index'))

# Virtual console placeholder
@app.route('/console/<int:device_id>', methods=['GET'])
def console_device(device_id):
    device = session.query(Device).get(device_id)
    if not device:
        return "Device not found", 404
    return f"Console view for {device.hostname} (Port: {device.port})"


if __name__ == '__main__':
    app.run()

