from flask import render_template, jsonify, request, session, redirect, make_response, flash, abort, send_file, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_wtf.csrf import CSRFError
from werkzeug.datastructures import FileStorage
from sqlalchemy import or_
from werkzeug.utils import secure_filename
import os
import uuid
import json

from forms import UploadItem
import oauth.model as mod
from init_app import app

from data import db_session
from data.users import User
from data.subcategories import SubCat
from data.items import Item

import auth

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

def cats() -> dict:
    with open('categories.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    

@app.after_request
def authorize(response):
    if 'logout' in session and session['logout']:
        del session['logout']
        return response
    
    if not current_user.is_authenticated:
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
    return jsonify({'success': False, 'code': 'csrf'})


@app.route('/')
def index():
    return redirect(f'/category/{list(cats().keys())[0]}')


@app.route('/category/<cat>')
def renderCategory(cat):
    db_sess = db_session.create_session()
    res = db_sess.query(SubCat).filter(SubCat.category == cat).all()
    return render_template(
        'index.html', category_name=cats()[cat],
        owner=cat, sub_categories=[(i.id, i.name) for i in res]
    )


@app.route('/category/<cat>/<id>')
def loadServicesCategory(cat, id):
    db_sess = db_session.create_session()
    items = db_sess.query(Item).filter(
        (Item.category_name == cat) & 
        (Item.subcategory_id == int(id)) & 
        (Item.buyer == None)
    ).all()
    return render_template(
        'catalog.html', items=[(str(i.id), i.name, i.about, str(i.amount), cat, id) for i in items],
        backed=f'/category/{cat}'
    )


@app.route('/category/<cat>/<sub_id>/<item_id>')
def loadItemCard(cat, sub_id, item_id):
    db_sess = db_session.create_session()
    item = db_sess.query(Item).filter(Item.id == int(item_id)).first()
    subcat = db_sess.query(SubCat).filter(SubCat.id == int(sub_id)).first()
    if item and subcat and cat in list(cats().keys()):
        owner = db_sess.query(User).filter(User.id == item.owner).first()
        buyer = db_sess.query(User).filter(User.id == item.buyer).first()
        if not item.buyer or current_user.id in [item.buyer, owner.id]:
            if request.args.get('action') == 'buy' and not item.buyer:
                if owner.id != current_user.id:
                    if current_user.balance >= item.amount:
                        current_user.balance -= item.amount
                        item.buyer, buyer = current_user.id, current_user
                        db_sess.commit()
                        flash('Товар куплен', 'success')

            return render_template(
                'card.html', item=item, cat=cats()[cat],
                subcat=subcat.name, owner=owner, buyer=buyer,
                backed=f'/category/{cat}/{sub_id}'
            )
        
    abort(404)


@app.route('/cabinet')
def loadCabinet():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        return render_template(
            'cabinet.html', balance=user.balance, backed='/'
        )
    return redirect('/')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if current_user.is_authenticated:
        form = UploadItem()

        item = Item()
        db_sess = db_session.create_session()
        edit = False

        if request.args.get('action') == 'edit':
            id = request.args.get('id')
            if id and id.isdigit():
                q = db_sess.query(Item).filter(Item.id == int(id)).first()
                if q and q.owner == current_user.id:
                    item = q
                    if request.method != 'POST':
                        form.name.data, form.description.data, form.content.data, form.price.data = (
                            item.name, item.about, item.content, item.amount
                        )
                        if item.file:
                            file = open(f'{app.config["ITEMS_FILES_PATH"]}/{item.file}', 'rb')
                            form.content_file.data = FileStorage(stream=file, filename=item.file)
                        photo = open(f'{app.config["ITEMS_IMAGES_PATH"]}/{id}.png', 'rb')
                        form.photo.data = FileStorage(stream=photo, filename=f'{id}.png')
                    edit = True

        if request.method == 'POST':
            item.name, item.about, item.content, item.amount, item.category_name, item.subcategory_id, item.owner = (
                form.name.data, form.description.data, form.content.data, int(form.price.data),
                form.category.data, int(form.subcategory.data), current_user.id
            )

            if form.content_file:
                file = form.content_file.data
                name = secure_filename(file.filename).split('.')
                name[0] = str(uuid.uuid4())
                name = '.'.join(name)
                file.save(os.path.join(app.config['ITEMS_FILES_PATH'], name))
                item.file = name
            
            if not edit:
                db_sess.add(item)

            db_sess.commit()
            form.photo.data.save(os.path.join(app.config['ITEMS_IMAGES_PATH'], f'{item.id}.png'))
        return render_template(
            'upload.html', form=form,
            action=f'/upload?action=edit&id={item.id}' if edit else '/upload', backed='/'
        )
    return redirect('/')


@app.route('/file/download/<filename>')
def download(filename):
    path = os.path.join(f"{app.config['ITEMS_FILES_PATH']}/{filename}")
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    abort(404)


@app.route('/api/v1/subcats/<cat>')
def getSubCats(cat):
    db_sess = db_session.create_session()
    res = db_sess.query(SubCat).filter(SubCat.category == cat).all()
    return jsonify({'success': True, 'data': [(str(i.id), i.name) for i in res]})


@app.route('/deposit', methods=['POST'])
def deposit():
    if current_user.is_authenticated:
        amount = request.form.get('amount')
        if amount:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            user.balance += int(amount)
            db_sess.commit()
            return render_template(
                'cabinet.html', balance=user.balance, backed='/'
            )
        m = 'invalid data'
    m = 'not auth'

    return jsonify({'success': False, 'message': m}), 401

@app.route('/search')
def search():
    target = request.args.get('query')
    db_sess = db_session.create_session()
    res = db_sess.query(Item).filter(
        or_(
            Item.name.ilike(f'%{target.lower()}%'),
            Item.name.ilike(f'%{target.capitalize()}%'),
            Item.about.ilike(f'%{target.lower()}%'),
            Item.about.ilike(f'%{target.capitalize()}%')
    )
    ).all()

    return render_template(
        'catalog.html', 
        items=[(str(i.id), i.name, i.about, str(i.amount), i.category_name, i.subcategory_id) for i in res], 
        backed='/'
    )


@app.route('/logout')
@login_required
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