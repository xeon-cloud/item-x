from flask import Flask
from flask_wtf.csrf import CSRFProtect
import os
import api.items as items
import api.alerts as alerts
import api.subcats as subcats
import api.chats as chats
import api.admin as admin
import auth
from flask_mail import Mail

app = Flask(__name__)
mail = Mail(app)

app.register_blueprint(items.blueprint)
app.register_blueprint(subcats.blueprint)
app.register_blueprint(alerts.blueprint)
app.register_blueprint(auth.blueprint)
app.register_blueprint(chats.blueprint)
app.register_blueprint(admin.blueprint)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['ITEMS_IMAGES_PATH'] = 'static/images/items'
app.config['ITEMS_FILES_PATH'] = 'static/item_files'
app.config['USERS_AVATARS_PATH'] = 'static/images/avatars'
app.config['JSON_SORT_KEYS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sagayaroslav2020@gmail.com'
app.config['MAIL_PASSWORD'] = 'Keks_bs11'
app.config['MAIL_DEFAULT_SENDER'] = 'sagayaroslav2020@gmail.com'

if not os.path.exists(app.config['ITEMS_IMAGES_PATH']):
    os.makedirs(app.config['ITEMS_IMAGES_PATH'])

if not os.path.exists(app.config['ITEMS_FILES_PATH']):
    os.makedirs(app.config['ITEMS_FILES_PATH'])

if not os.path.exists(app.config['USERS_AVATARS_PATH']):
    os.makedirs(app.config['USERS_AVATARS_PATH'])