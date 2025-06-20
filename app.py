# app.py
from connect_app import ConnectApp

if __name__ == '__main__':
    app = ConnectApp()
    app.run(host='0.0.0.0', port=5000)
