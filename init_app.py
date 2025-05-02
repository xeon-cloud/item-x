from flask import Flask
from flask_wtf.csrf import CSRFProtect
import os
import items_api

app = Flask(__name__)
app.register_blueprint(items_api.blueprint)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['ITEMS_IMAGES_PATH'] = 'static/images/items'
app.config['ITEMS_FILES_PATH'] = 'static/item_files'
app.config['USERS_AVATARS_PATH'] = 'static/images/avatars'

if not os.path.exists(app.config['ITEMS_IMAGES_PATH']):
    os.makedirs(app.config['ITEMS_IMAGES_PATH'])

if not os.path.exists(app.config['ITEMS_FILES_PATH']):
    os.makedirs(app.config['ITEMS_FILES_PATH'])

if not os.path.exists(app.config['USERS_AVATARS_PATH']):
    os.makedirs(app.config['USERS_AVATARS_PATH'])