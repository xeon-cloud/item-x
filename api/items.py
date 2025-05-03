from flask import Blueprint, jsonify, request, abort
from data import db_session
from data.items import Item
from flask_login import current_user, login_required

blueprint = Blueprint('items_api', __name__, template_folder='templates')


def item_to_dict(item: Item):
    return {
        'id': item.id,
        'name': item.name,
        'about': item.about,
        'owner': item.owner,
        'category_name': item.category_name,
        'subcategory_id': item.subcategory_id,
        'amount': item.amount
    }


@blueprint.route('/api/post_user_items', methods=['POST'])
@login_required
def post_user_items():
    """Создание нового товара"""
    db_sess = db_session.create_session()

    data = request.get_json()
    if not data or not 'name' in data:
        return jsonify({'success': False, 'message': 'Missing required field: name'}), 400

    new_item = Item(
        name=data['name'],
        about=data.get('about'),
        owner=str(current_user.id),
        category_name=data.get('category_name'),
        subcategory_id=data.get('subcategory_id'),
        amount=data.get('amount')
    )
    db_sess.add(new_item)
    try:
        db_sess.commit()
        return jsonify({'success': True, 'message': 'Item created', 'id': new_item.id}), 201
    except Exception as e:
        db_sess.rollback()
        return jsonify({'success': False, 'message': 'Failed to create item', 'error': str(e)}), 500


@blueprint.route('/api/get_user_items', methods=['GET'])
@login_required
def get_user_items():
    """Получение списка товаров пользователя"""
    db_sess = db_session.create_session()

    items = db_sess.query(Item).filter(Item.owner == str(current_user.id)).all()
    return jsonify({'success': True, 'data': [item_to_dict(item) for item in items]})


@blueprint.route('/api/update_user_items/<int:item_id>', methods=['PUT', 'DELETE'])
@login_required
def update_user_item(item_id):
    """Обновление товара пользователя."""
    db_sess = db_session.create_session()
    item = db_sess.query(Item).filter(Item.id == item_id, Item.owner == str(current_user.id)).first()
    if not item:
        return jsonify({'success': False, 'message': 'Item not found or not owned by user'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    if 'name' in data:
        item.name = data['name']
    if 'about' in data:
        item.about = data['about']
    if 'category_name' in data:
        item.category_name = data['category_name']
    if 'subcategory_id' in data:
        item.subcategory_id = data['subcategory_id']
    if 'amount' in data:
        item.amount = data['amount']

    try:
        db_sess.commit()
        return jsonify({'success': True, 'message': 'Item updated'}), 200
    except Exception as e:
        db_sess.rollback()
        return jsonify({'success': False, 'message': 'Failed to update item', 'error': str(e)}), 500


@blueprint.route('/api/del_user_items/<int:item_id>', methods=['DELETE'])
@login_required
def del_user_item(item_id):
    """Удаление товара пользователя."""
    db_sess = db_session.create_session()
    item = db_sess.query(Item).filter(Item.id == item_id, Item.owner == str(current_user.id)).first()
    if not item:
        return jsonify({'success': False, 'message': 'Item not found or not owned by user'}), 404

    try:
        db_sess.delete(item)
        db_sess.commit()
        return '', 204
    except Exception as e:
        db_sess.rollback()
        return jsonify({'success': False, 'message': 'Failed to delete item', 'error': str(e)}), 500
    
@blueprint.errorhandler(404)
def page_not_found(e):
    abort(404)