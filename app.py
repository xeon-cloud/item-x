from flask import Flask, render_template, jsonify, url_for, request, session, redirect, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_socketio import SocketIO, join_room, leave_room, send
import random

import os
import forms
import oauth.yandex as ya
import oauth.model as mod
import hcaptcha.model as cap
from hcaptcha.config import HC_SITE_KEY

from data import db_session
from data.users import User
from data.subcategories import Games, Services
from data.items import Item

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
# csrf = CSRFProtect(app)

socketio = SocketIO(app)
rooms = {}

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({'code': 'csrf'})

@app.route('/')
def index():
    return redirect('/games')


@app.route('/games')
def games():
    db_sess = db_session.create_session()
    login_user(db_sess.query(User).filter(User.id == 1).first())
    res = db_sess.query(Games).all()
    return render_template(
        'index.html', category_name='Игры',
        owner='games', sub_categories=[(i.id, i.name) for i in res]
    )

@app.route('/services')
def services():
    db_sess = db_session.create_session()
    res = db_sess.query(Services).all()
    return render_template(
        'index.html', category_name='Сервисы',
        owner='services', sub_categories=[(i.id, i.name) for i in res]
    )


@app.route('/<cat>/<id>')
def loadServicesCategory(cat, id):
    db_sess = db_session.create_session()
    res = db_sess.query(Item).filter(Item.category_name == cat and Item.subcategory_id == int(id))
    return render_template(
        'catalog.html', category=cat, subcategory=id,
        items=[(str(i.id), i.name, i.about) for i in res], backed=f'/{cat}'
    )


@app.route('/register', methods=['GET', 'POST'])
def sign_up():
    form = forms.Registration()
    if form.validate_on_submit():
        data = request.form
        captchaResponse = data.get('h-captcha-response')
        if captchaResponse and cap.validateCaptcha(captchaResponse):
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.username == form.username.data).first():
                flash('Имя пользователя уже существует', 'error')
            elif db_sess.query(User).filter(User.email == form.email.data).first():
                flash('Почта уже занята', 'error')
            else:
                user = User()
                ya_id = int(session['id']) if 'id' in session else None
                user.username, user.email, user.hashed_password, user.ya_id = (form.username.data, form.email.data,
                                                                            mod.encodePassword(form.password.data), ya_id)
                db_sess = db_session.create_session()
                db_sess.add(user)
                db_sess.commit()
                login_user(user)
                return redirect('/')
        else:
            flash('Пройдите проверку на робота!', 'error')

    elif 'id' in session and 'username' in session and 'email' in session:
            form.username.data, form.email.data = session['username'], session['email']
    return render_template(
        'auth/register.html', form=form,
        ya_auth_url=ya.renderAuthUrl(), hc_key=HC_SITE_KEY
    )

@app.route('/login', methods=['GET', 'POST'])
def sign_in():
    form = forms.Login()
    if form.validate_on_submit():
        data = request.form
        captchaResponse = data.get('h-captcha-response')
        if captchaResponse and cap.validateCaptcha(captchaResponse):
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.username == form.username.data).first()
            if user and mod.encodePassword(form.password.data) == user.hashed_password:
                login_user(user)
                return redirect('/')
            else:
                flash('Неверно указан логин или пароль', 'error')
        else:
            flash('Пройдите проверку на робота!', 'error')
            
    return render_template(
        'auth/login.html', form=forms.Login(),
        ya_auth_url=ya.renderAuthUrl(), hc_key=HC_SITE_KEY
    )

@app.route('/callback')
def callback():
    code = request.args.get('code')
    data = ya.authorizeUser(code)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.ya_id == int(data['id'])).first()
    if user:
        login_user(user)
        return redirect('/')
    session['id'], session['username'], session['email'] = data['id'], data['login'], data['default_email']
    return redirect('/register')


def generate_room_code(length: int, existing_codes: list[str]) -> str:
    while True:
        code_chars = [random.choice(["a", "b", "c", "d", "f"]) for _ in range(length)]
        code = ''.join(code_chars)
        if code not in existing_codes:
            return code


@app.route('/chat', methods=["GET", "POST"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get('name')
        create = request.form.get('create', False)
        code = request.form.get('code')
        join = request.form.get('join', False)
        if not name:
            return render_template('home.html', error="Name is required", code=code)
        if create != False:
            room_code = generate_room_code(6, list(rooms.keys()))
            new_room = {
                'members': 0,
                'messages': []
            }
            rooms[room_code] = new_room
        if join != False:
            # no code
            if not code:
                return render_template('home.html', error="Please enter a room code to enter a chat room", name=name)
            # invalid code
            if code not in rooms:
                return render_template('home.html', error="Room code invalid", name=name)
            room_code = code
        session['room'] = room_code
        session['name'] = name
        return redirect(url_for('room'))
    else:
        return render_template('home.html')


@app.route('/room')
def room():
    room = session.get('room')
    name = session.get('name')
    if name is None or room is None or room not in rooms:
        return redirect(url_for('home'))
    messages = rooms[room]['messages']
    return render_template('room.html', room=room, user=name, messages=messages)


@socketio.on('connect')
def handle_connect():
    name = session.get('name')
    room = session.get('room')
    if name is None or room is None:
        return
    if room not in rooms:
        leave_room(room)
    join_room(room)
    send({
        "sender": "",
        "message": f"{name} has entered the chat"
    }, to=room)
    rooms[room]["members"] += 1


@socketio.on('message')
def handle_message(payload):
    room = session.get('room')
    name = session.get('name')
    if room not in rooms:
        return
    message = {
        "sender": name,
        "message": payload["message"]
    }
    send(message, to=room)
    rooms[room]["messages"].append(message)


@socketio.on('disconnect')
def handle_disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
        send({
        "message": f"{name} has left the chat",
        "sender": ""
    }, to=room)


if __name__ == '__main__':
    db_session.global_init("db/database.sqlite")
    app.run(port=8080, host='127.0.0.1', debug=True)