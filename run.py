from flask import render_template, jsonify, request, session, redirect, make_response
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_wtf.csrf import CSRFError

import oauth.model as mod
from init_app import app

from data import db_session
from data.users import User
from data.subcategories import Games, Services
from data.items import Item

import auth

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.after_request
def authorize(response):
    if 'logout' in session and session['logout']:
        del session['logout']
        return response
    
    auth_token = request.cookies.get('auth_token')
    if auth_token:
        try:
            user_id = mod.decodeAuthToken(auth_token)['id']
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == user_id).first()
            if user:
                login_user(user)
        except Exception as e:
            print(f"Authorization error: {e}")
    
    return response

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({'code': 'csrf'})

@app.route('/')
def index():
    return redirect('/games')


@app.route('/games')
def games():
    db_sess = db_session.create_session()
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
        items=[(str(i.id), i.name, i.about, str(i.amount) ) for i in res], backed=f'/{cat}'
    )

@app.route('/<cat>/<sub_id>/<item_id>')
def loadItemCard(cat, sub_id, item_id):
    db_sess = db_session.create_session()
    return render_template(
        'card.html', backed=f'/{cat}/{sub_id}'
    )

@app.route('/cabinet')
def loadCabinet():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        return render_template(
            'cabinet.html', balance=user.balance, backed='/'
        )
    return redirect('/')



@app.route('/deposit', methods=['POST'])
def deposit():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.balance += int(request.form.get('amount'))
    db_sess.commit()
    return render_template(
        'cabinet.html', balance=user.balance, backed='/'
    )

@app.route('/logout')
def logout():
    logout_user()
    session['logout'] = True
    response = make_response(
        redirect('/')
    )
    response.delete_cookie('auth_token', path='/')
    return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    db_session.global_init("db/database.sqlite")
    app.run(port=8080, host='127.0.0.1', debug=True)