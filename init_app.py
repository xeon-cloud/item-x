from flask import Flask
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['ITEMS_IMAGES_PATH'] = 'static/images/items'
app.config['ITEMS_FILES_PATH'] = 'static/item_files'
app.config['USERS_AVATARS_PATH'] = 'static/images/avatars'