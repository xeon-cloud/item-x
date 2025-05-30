from flask import Flask
import os
import api.user as user
import api.items as items
import api.alerts as alerts
import api.subcats as subcats
import api.chats as chats
import api.admin as admin
import auth

app = Flask(__name__)

app.register_blueprint(user.blueprint)
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

if not os.path.exists(app.config['ITEMS_IMAGES_PATH']):
    os.makedirs(app.config['ITEMS_IMAGES_PATH'])

if not os.path.exists(app.config['ITEMS_FILES_PATH']):
    os.makedirs(app.config['ITEMS_FILES_PATH'])

if not os.path.exists(app.config['USERS_AVATARS_PATH']):
    os.makedirs(app.config['USERS_AVATARS_PATH'])
