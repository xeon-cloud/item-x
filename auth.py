from flask import request, session, flash, make_response, render_template, redirect

import forms
from init_app import app

import oauth.model as mod
import oauth.yandex as ya

from hcaptcha.config import HC_SITE_KEY
import hcaptcha.model as cap

from data import db_session
from data.users import User


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
                response = make_response(
                    redirect('/')
                )
                response.set_cookie('auth_token', mod.createAuthToken({'id': user.id}))
                return response
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

@app.route('/callback')
def callback():
    code = request.args.get('code')
    data = ya.authorizeUser(code)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.ya_id == int(data['id'])).first()
    if user:
        response = make_response(
                    redirect('/')
        )
        response.set_cookie('auth_token', mod.createAuthToken({'id': user.id}))
        return response
    session['id'], session['username'], session['email'] = data['id'], data['login'], data['default_email']
    return redirect('/register')