from flask import Blueprint, jsonify, request
import base64
import uuid
import os
import json

from api.http_auth import auth

from data import db_session
from data.items import Item
from data.subcategories import SubCat


blueprint = Blueprint('items', __name__, template_folder='templates')

def cats() -> dict:
    with open('categories.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
def subCats() -> list:
    db_sess = db_session.create_session()
    res = db_sess.query(SubCat).all()
    return [i.id for i in res]

def item_to_dict(item: Item):
    return {
        'id': item.id,
        'name': item.name,
        'about': item.about,
        'content': item.content,
        'categoryName': item.category_name,
        'subCategoryId': item.subcategory_id,
        'amount': item.amount,
        'createdDate': item.created_date,
        'isPurchased': True if item.buyer else False
    }

def saveBase64(base64String, name, path):
    """Сохраняем файл по base64 строчке"""
    if base64String.startswith('data:'):
        base64String = base64String.split(',')[1]

    try:
        fileData = base64.b64decode(base64String)
    except Exception as e:
        print(f"Error decoding base64: {e}")
        return

    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print(f"Created directory: {path}")
        except OSError as e:
            print(f"Error creating directory {path}: {e}")
            return

    try:
        filepath = os.path.join(path, name)
        with open(filepath, 'wb') as f:
            f.write(fileData)
        print(f"File saved to: {filepath}")
    except Exception as e:
        print(f"Error saving file to {filepath}: {e}")


@blueprint.route('/api/items/create', methods=['POST'])
@auth.login_required
def createItems():
    """Создание нового товара"""
    db_sess = db_session.create_session()
    try:
        data: dict = request.get_json()
        if not data or not 'name' in data:
            raise Exception('Missing required field: name')

        if not isinstance(data.get('amount'), int):
            raise Exception('Invalid amount type')

        if not data.get('image'):
            raise Exception('Item image required')
        
        if data.get('categoryName') not in cats().keys():
            raise Exception(f'Сategory must be one of: {", ".join(list(cats().keys()))}')
        
        if data.get('subCategoryId'):
            if isinstance(data.get('subCategoryId'), int):
                if not data.get('subCategoryId') in subCats():
                    raise Exception('Non-existent SubCategory id')
            else:
                raise Exception('Invalid SubCategory id type')
        else:
            raise Exception('SubCategory id required')

        item = Item(
            name=data['name'],
            about=data.get('about'),
            owner=str(auth.current_user().id),
            content=data.get('content'),
            category_name=data.get('categoryName'),
            subcategory_id=data.get('subCategoryId'),
            amount=data.get('amount')
        )

        contentFileData, extension = data.get('contentFile'), data.get("extension")
        if contentFileData:
            if extension:
                file_name = f'{str(uuid.uuid4())}.{extension}'
                item.file = file_name
                saveBase64(contentFileData, file_name, 'static/item_files')
            else:
                raise Exception('Extension for content file required')

        db_sess.add(item)
        db_sess.commit()

        image_data = data.get('image')
        saveBase64(image_data, f'{item.id}.png', 'static/images/items')

        db_sess.refresh(item)
        return jsonify({
            'success': True,
            'message': 'Item created',
            'data': {
                'id': item.id,
                'url': f'/category/{data.get("categoryName")}/{data.get("subCategoryId")}/{item.id}'
            }
        }), 201

    except Exception as e:
        db_sess.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to create item',
            'error': str(e)
        }), 500
    finally:
        db_sess.close()

@blueprint.route('/api/items', methods=['GET'])
@auth.login_required
def getItems():
    """Получение списка товаров пользователя"""
    db_sess = db_session.create_session()

    items = db_sess.query(Item).filter(Item.owner == str(auth.current_user().id)).all()
    return jsonify({
        'success': True,
        'data': [item_to_dict(item) for item in items]
    })


@blueprint.route('/api/items/update/<int:item_id>', methods=['POST', 'PUT'])
@auth.login_required
def updateItem(item_id):
    try:
        """Обновление товара пользователя."""
        db_sess = db_session.create_session()
        item = db_sess.query(Item).filter(Item.id == item_id, Item.owner == str(auth.current_user().id)).first()
        if not item:
            raise Exception('Item not found or not owned by user')
        
        if item.buyer:
            raise Exception('Item was purchased')

        data: dict = request.get_json()
        if not data:
            raise Exception('Missing data')

        if data.get('name'):
            item.name = data.get('name')

        if data.get('about'):
            item.about = data.get('about')

        if data.get('content'):
            item.about = data['content']

        contentFileData, extension = data.get('contentFile'), data.get("extension")
        if contentFileData:
            if extension:
                file_name = f'{str(uuid.uuid4())}.{extension}'
                item.file = file_name
                saveBase64(contentFileData, file_name, 'static/item_files')
            else:
                raise Exception('Extension for content file required')
            
        if data.get('categoryName'):
            if data.get('categoryName') in cats().keys():
                item.category_name = data.get('categoryName')
            else:
                raise Exception(f'Сategory must be one of: {", ".join(list(cats().keys()))}')

        if data.get('subCategoryId'):
            item.subcategory_id = data.get('subCategoryId')

        if data.get('amount'):
            item.amount = data.get('amount')

        if data.get('image'):
            saveBase64(data.get('image'), f'{item.id}.png', 'static/images/items')

        db_sess.commit()
        return jsonify({
            'success': True,
            'message': 'Item updated'
        }), 200
    
    except Exception as e:
        db_sess.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update item',
            'error': str(e)
        }), 500


@blueprint.route('/api/items/delete/<int:item_id>', methods=['POST', 'DELETE'])
@auth.login_required
def deleteItem(item_id):
    try:
        """Удаление товара пользователя."""
        db_sess = db_session.create_session()
        item = db_sess.query(Item).filter(Item.id == item_id, Item.owner == str(auth.current_user().id)).first()
        if not item:
            raise Exception('Item not found or not owned by user')
        if item.buyer:
            raise Exception('Item was purchased')
        db_sess.delete(item)
        db_sess.commit()
        return jsonify({
            'success': True,
            'message': 'Item deleted'
        })
    
    except Exception as e:
        db_sess.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to delete item',
            'error': str(e)
        }), 500