from flask import render_template, jsonify, request, session, redirect, make_response, flash, abort, send_file, url_for
from flask.json import provider
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_wtf.csrf import CSRFError
from werkzeug.datastructures import FileStorage
from wtforms.validators import DataRequired
from sqlalchemy import or_
from werkzeug.utils import secure_filename
import time
import os
import uuid
import json
import io

from forms import UploadItem
import oauth.model as mod
from init_app import app, mail

from data.purchases import Purchase

import converter
from data import db_session
from data.users import User
from data.subcategories import SubCat
from data.items import Item
from data.alerts import Alert, RenderAlerts
from data.holds import Hold, targetHolds

import api.chats as chats

provider.DefaultJSONProvider.sort_keys = False
provider.DefaultJSONProvider.ensure_ascii = False

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    db_sess.close()
    return user


render_alerts = RenderAlerts()

def cats() -> dict:
    with open('categories.json', 'r', encoding='utf-8') as f:
        return json.load(f)


@app.before_request
def authorize():
    if 'logout' in session and session['logout']:
        logout_user()
        del session['logout']
        return
    
    auth_token = request.cookies.get('auth_token')
    if auth_token:
        try:
            db_sess = db_session.create_session()
            user_id = mod.decodeAuthToken(auth_token)['id']
            user = db_sess.query(User).filter(User.id == user_id).first()
            if user:
                if current_user.is_anonymous:
                    login_user(user)
                    return
                user.last_activity = int(time.time())
                targetHolds(current_user.id)
                db_sess.commit()
        except Exception as e:
            db_sess.rollback()
            print(f"Authorization error: {e}")
        finally:
            db_sess.close()


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({'success': False, 'code': 'csrf'})


@app.route('/')
def index():
    # если вход через поддержку то пинаем работать
    if current_user.is_authenticated and current_user.id == 0:
        return redirect('/chats')
    return redirect('/category/services')


@app.route('/chats')
def chat():
    return render_template(
        'chats.html',
        data=chats.getDialogs(),
        active_user=None,
        backed='/'
    )

@app.route('/chat/<int:id>')
def userChat(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if not user:
        return redirect('/chats')
    messages, dialogs = chats.getMessages(id), chats.getDialogs()
    return render_template(
        'chats.html',
        data=dialogs,
        active_chat=messages,
        active_user=user,
        backed='/'
    )


@app.route('/category/<cat>')
def renderCategory(cat):
    # если вход через поддержку то пинаем работать
    if current_user.is_authenticated and current_user.id == 0:
        return redirect('/chats')
    if cat not in cats().keys():
        abort(404)
    db_sess = db_session.create_session()
    res = db_sess.query(SubCat).filter(SubCat.category == cat).all()
    db_sess.close()
    return render_template(
        'index.html', category_name=cats()[cat],
        owner=cat, categories=cats().items(), sub_categories=[(i.id, i.name) for i in res]
    )


@app.route('/category/<cat>/<int:id>')
def loadServicesCategory(cat, id):
    # если вход через поддержку то пинаем работать
    if current_user.is_authenticated and current_user.id == 0:
        return redirect('/chats')
    db_sess = db_session.create_session()
    items = db_sess.query(Item).filter(
        (Item.category_name == cat) & 
        (Item.subcategory_id == int(id)) & 
        (Item.buyer == None)
    ).all()

    # режим фильтра
    mnPrice, mxPrice = request.args.get('minPrice'), request.args.get('maxPrice')
    if mnPrice and mxPrice and mnPrice.isdigit() and mnPrice.isdigit() and int(mnPrice) <= int(mxPrice):
        for i, j in enumerate(items):
            amount = j.amount
            if not (amount >= int(mnPrice) and amount <= int(mxPrice)):
                items.pop(i)

    dateType = request.args.get('dateType')
    items = sorted(
        items, key=lambda item: item.created_date,
        reverse=False if dateType == 'old' else True
    )

    db_sess.close()

    return render_template(
        'catalog.html', items=[(str(i.id), i.name, i.about, str(i.amount), cat, id) for i in items],
        backed=f'/category/{cat}'
    )



@app.route('/cabinet/purchase_history')
@login_required
def purchase_history():
    db_sess = db_session.create_session()
    purchases = db_sess.query(Purchase).filter(Purchase.user_id == current_user.id).order_by(Purchase.purchase_date.desc()).all()
    db_sess.close()
    return render_template('purchases_history.html', purchases=purchases, backed='/cabinet')


@app.route('/category/<cat>/<sub_id>/<item_id>')
def loadItemCard(cat, sub_id, item_id):
    # если вход через поддержку то пинаем работать
    if current_user.is_authenticated and current_user.id == 0:
        return redirect('/chats')
    db_sess = db_session.create_session()
    try:
        item = db_sess.query(Item).filter(Item.id == int(item_id)).first()
        subcat = db_sess.query(SubCat).filter(SubCat.id == int(sub_id)).first()
        if item and subcat and cat in list(cats().keys()):
            owner = db_sess.query(User).filter(User.id == item.owner).first()
            buyer = db_sess.query(User).filter(User.id == item.buyer).first()
            if not item.buyer or current_user.id in [item.buyer, owner.id]:
                if request.args.get('action') == 'buy' and not item.buyer:
                    # пинаем на авторизацию если лезет покупать при гостевом входе
                    if current_user.is_anonymous:
                        return redirect('/auth/login')
                    
                    if owner.id != current_user.id:
                        if current_user.balance >= item.amount:
                            buyer = db_sess.query(User).filter(User.id == current_user.id).first()
                            buyer.balance = buyer.balance - item.amount
                            owner.hold += item.amount
                            item.buyer, buyer = buyer.id, current_user

                            render = render_alerts.purchase

                            db_sess.add(Purchase(
                                user_id=current_user.id,
                                item_id=item.id,
                                price=item.amount,
                                item_name=item.name,
                                item_description=item.about,
                                item_image=f'/static/images/items/{item.id}.png',
                                item_url=f'/category/{cat}/{sub_id}/{item.id}'
                            ))
                            db_sess.add(Alert(
                                owner=item.owner,
                                header=render[0],
                                content=render[1].format(
                                    current_user.id, current_user.username,
                                    cat, sub_id, item_id, item.name, item.amount
                                )
                            ))
                            db_sess.add(Hold(
                                user_id=owner.id,
                                amount=item.amount,
                                end_date=int(time.time() + 86400)
                            ))
                            db_sess.commit()
                            flash('Товар куплен', 'success')
                        else:
                            flash('На балансе недостаточно средств', 'danger')
                return render_template(
                    'card.html', item=item, cat=cats()[cat],
                    subcat=subcat.name, owner=owner, buyer=buyer,
                    backed=f'/category/{cat}/{sub_id}'
                )
        
        abort(404)
    except Exception as e:
        db_sess.rollback()
        print(f'Item Error: {e}')
        return jsonify({'err': str(e)})
    finally:
        db_sess.close()


@app.route('/cabinet')
def loadCabinet():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        sells = db_sess.query(Item).filter(Item.owner == user.id and Item.buyer).all()
        count_sells = len(sells)
        sum_sells = sum([i.amount for i in sells])

        db_sess.close()
        return render_template(
            'cabinet.html',
            balance_rub=user.balance, balance_usd=f'{converter.convert(user.balance):.2f}',
            hold_rub=user.hold, hold_usd=f'{converter.convert(user.hold):.2f}',
            count_sells=count_sells, sum_sells=f'{sum_sells}₽ (${converter.convert(sum_sells):.2f})',
            date_register=user.format_date(),
            backed='/'
        )
    return redirect('/')

@app.route('/user/<int:id>')
def loadUser(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if not user or id == 0:
        abort(404)

    sells = db_sess.query(Item).filter(Item.owner == user.id and Item.buyer).all()
    count_sells = len(sells)
    sum_sells = sum([i.amount for i in sells])

    return render_template(
        'profile.html',
        user=user, count_sells=count_sells,
        sum_sells=f'{sum_sells}₽ (${converter.convert(sum_sells):.2f})',
        date_register=user.format_date(), now=int(time.time()),
        backed='/'
    )


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if current_user.is_authenticated:
        # если вход через поддержку то пинаем работать
        if current_user.id == 0:
            return redirect('/chats')
        form = UploadItem()
        db_sess = db_session.create_session()
        item = Item()

        edit = False
        if request.args.get('action') == 'edit':
            id = request.args.get('id')
            if id and id.isdigit():
                req = db_sess.query(Item).filter(Item.id == int(id)).first()
                if req and req.owner == current_user.id and not req.buyer:
                    # динамически убираем валидатор у фото в режиме едита
                    class F(UploadItem):
                        pass

                    validators = F.photo.kwargs.get('validators')
                    for validator in validators:
                        if isinstance(validator, DataRequired):
                            validators.remove(validator)

                    form = F()
                    
                    item = req
                    if request.method != 'POST':
                        for subcat in db_sess.query(SubCat).filter(SubCat.category == item.category_name).all():
                            form.subcategory.choices.append((subcat.id, subcat.name))
                            
                        form.name.data, form.description.data, form.content.data, form.price.data, form.category.data, form.subcategory.data = (
                            item.name, item.about, item.content, item.amount, item.category_name, str(item.subcategory_id)
                        )
    
                        if item.file:
                            file_path = f'{app.config["ITEMS_FILES_PATH"]}/{item.file}'
                            with open(file_path, 'rb') as f:
                                form.content_file.data = FileStorage(stream=io.BytesIO(f.read()), filename=item.file)

                        photo_path = f'{app.config["ITEMS_IMAGES_PATH"]}/{id}.png'
                        with open(photo_path, 'rb') as f:
                            form.photo.data = FileStorage(stream=io.BytesIO(f.read()), filename=f'{id}.png')

                    edit = True
                else:
                    abort(404)

        if request.method == 'POST':
            item.name, item.about, item.content, item.amount, item.category_name, item.subcategory_id, item.owner = (
                form.name.data, form.description.data, form.content.data, int(form.price.data),
                form.category.data, int(form.subcategory.data), current_user.id
            )

            if form.content_file.data:
                file = form.content_file.data
                name = secure_filename(file.filename).split('.')
                name[0] = str(uuid.uuid4())
                name = '.'.join(name)
                file.save(os.path.join(app.config['ITEMS_FILES_PATH'], name))
                item.file = name

            if not edit:
                db_sess.add(item)

            db_sess.commit()

            if form.photo.data:
                form.photo.data.save(os.path.join(app.config['ITEMS_IMAGES_PATH'], f'{item.id}.png'))

            flash(f'Товар успешно {"выставлен" if not edit else "изменен"}', 'success')
            return redirect('cabinet/my_items')

        for target, name in cats().items():
            form.category.choices.append((target, name))
        
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


@app.route('/deposit', methods=['POST'])
@login_required
def deposit():
    # если вход через поддержку то пинаем работать
    if current_user.id == 0:
        return redirect('/chats')
    amount = request.form.get('amount')
    if amount:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.balance += int(amount)
        db_sess.commit()
        flash(f'Успешное пополнение: {amount}₽', 'success')
        return redirect('/cabinet')
    m = 'invalid data'

    return jsonify({'success': False, 'message': m}), 401


@app.route('/search')
def search():
    # если вход через поддержку то пинаем работать
    if current_user.is_authenticated and current_user.id == 0:
        return redirect('/chats')
    target = request.args.get('query')
    db_sess = db_session.create_session()
    items = db_sess.query(Item).filter(
        or_(
            Item.name.ilike(f'%{target.lower()}%'),
            Item.name.ilike(f'%{target.capitalize()}%'),
            Item.about.ilike(f'%{target.lower()}%'),
            Item.about.ilike(f'%{target.capitalize()}%')
    )
    ).all()
    db_sess.close()

    # режим фильтра
    mnPrice, mxPrice = request.args.get('minPrice'), request.args.get('maxPrice')
    if mnPrice and mxPrice and mnPrice.isdigit() and mnPrice.isdigit() and int(mnPrice) <= int(mxPrice):
        for i, j in enumerate(items):
            if not (j.amount >= int(mnPrice) and j.amount <= int(mxPrice)):
                items.pop(i)

    dateType = request.args.get('dateType')
    items = sorted(
        items, key=lambda item: item.created_date,
        reverse=False if dateType == 'old' else True
    )

    return render_template(
        'catalog.html',
        items=[(str(i.id), i.name, i.about, str(i.amount), i.category_name, i.subcategory_id, i.created_date) for i in items],
        backed='/'
    )


@app.route('/logout')
@login_required
def logout():
    session['logout'] = True
    response = make_response(
        redirect('/')
    )
    response.delete_cookie('auth_token')
    return response


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/cabinet/my_items')
@login_required
def my_items():
    # если вход через поддержку то пинаем работать
    if current_user.id == 0:
        return redirect('/chats')
    db_sess = db_session.create_session()
    items = db_sess.query(Item).filter(Item.owner == current_user.id).all()
    return render_template('my_items.html', items=items, backed='/cabinet')


if __name__ == '__main__':
    db_session.global_init("db/database.sqlite")
    app.run(port=8080, host='0.0.0.0', debug=True)