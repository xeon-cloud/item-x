from flask import Flask
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY