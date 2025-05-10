from flask import Blueprint, request, session, flash, make_response, render_template, redirect, abort
from flask_login import current_user
import requests
from PIL import Image
from io import BytesIO
import os

import forms

import oauth.model as mod
import oauth.yandex as ya

from hcaptcha.config import HC_SITE_KEY
import hcaptcha.model as cap

from data import db_session
from data.users import User
from api.chats import sendMessage


blueprint = Blueprint('auth', __name__, template_folder='templates')


@blueprint.route('/auth/register', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect('/')
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
                if 'ya_login' in session and session['ya_login']:
                    ya_id = int(session['id'])
                    avatar = 1 if session['avatar'] else 0
                else:
                    ya_id = None
                    avatar = 0
                
                user.username, user.email, user.ya_id, user.avatar = (form.username.data, form.email.data, ya_id, avatar)
                user.set_password(form.password.data)

                db_sess = db_session.create_session()
                db_sess.add(user)
                db_sess.commit()
                
                if avatar == 1:
                    response = requests.get(f'https://avatars.yandex.net/get-yapic/{session["avatar"]}/islands-200')
                    image = Image.open(BytesIO(response.content))
                    save_path = os.path.join('static', 'images', 'avatars', f'{user.id}.png')
                    image.save(save_path, format='PNG')

                response = make_response(
                    redirect('/')
                )
                response.set_cookie('auth_token', mod.createAuthToken({'id': user.id}))
                sendMessage(
                    user.id,
                    'Здравствуйте! Спасибо за регистрацию на нашем сервисе.',
                    as_support=True
                )
                return response
        else:
            flash('Пройдите проверку на робота!', 'error')

    elif 'id' in session:
        form.username.data, form.email.data = session['username'], session['email']

    return render_template(
        'auth/register.html', form=form,
        ya_auth_url=ya.renderAuthUrl(), hc_key=HC_SITE_KEY
    )


@blueprint.route('/auth/login', methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return redirect('/')
    form = forms.Login()
    if form.validate_on_submit():
        data = request.form
        captchaResponse = data.get('h-captcha-response')
        if captchaResponse and cap.validateCaptcha(captchaResponse):
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.username == form.username.data).first()
            if user and user.check_password(form.password.data):
                response = make_response(
                    redirect('/')
                )
                response.set_cookie('auth_token', mod.createAuthToken({'id': user.id}))
                return response
            else:
                flash('Неверно указан логин или пароль', 'error')
        else:
            flash('Пройдите проверку на робота!', 'error')
            
    return render_template(
        'auth/login.html', form=forms.Login(),
        ya_auth_url=ya.renderAuthUrl(), hc_key=HC_SITE_KEY
    )


@blueprint.route('/auth/callback', methods=['GET', 'POST'])
def callback():
    try:
        code = request.args.get('code')  
        data = ya.authorizeUser(code)
    except Exception as e:
        print(f'Callback Error - {e}')
        abort(403)

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.ya_id == int(data['id'])).first()
    if user:
        response = make_response(
            redirect('/')
        )
        response.set_cookie('auth_token', mod.createAuthToken({'id': user.id}))
        return response
    session['ya_login'] = True
    session['id'], session['username'], session['email'] = data['id'], data['login'], data['default_email']
    session['avatar'] = data['default_avatar_id'] if 'default_avatar_id' in data else None

    return redirect('/auth/register')