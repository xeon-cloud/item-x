from flask import Blueprint, jsonify, request, redirect
from flask_login import current_user, login_required
import json
import datetime

from data import db_session
from data.users import User


blueprint = Blueprint('chats', __name__, template_folder='templates')

def getData() -> list:
    with open('chats.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
def dumpData(data):
    with open('chats.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def getUnreads():
    data = getData()
    total = 0
    for i in data:
        if current_user.id in i['users']:
            for j in i['messages']:
                if j['to'] == current_user.id:
                    if j['unread']:
                        total += 1
    return total


def getMessages(id):
    data = getData()
    for i in data:
        if current_user.id in i['users'] and id in i['users']:
            for j in i['messages']:
                if j['to'] == current_user.id:
                    j['unread'] = False
            dumpData(data)
            return i['messages']
    return []

def getDialogs():
    db_sess = db_session.create_session()
    data = getData()
    res = []
    for i in data:
        if current_user.id in i['users']:
            unread = 0
            for j in i['messages']:
                if j['unread'] and j['to'] == current_user.id:
                    unread += 1
            i['users'].remove(current_user.id)
            res.append((db_sess.query(User).filter(User.id == i['users'][0]).first(), unread))
    db_sess.close()
    return res

def sendMessage(id, message, as_support=False):
    data = getData()
    owner = current_user.id if not as_support else 0
    messageObj = {
        'from': owner,
        'to': id,
        'content': message,
        'unread': True,
        'time': datetime.datetime.now().strftime("%d %B %H:%M")
    }
    exist = False
    for i, j in enumerate(data):
        if owner in j['users'] and id in j['users']:
            j['messages'].append(messageObj)
            exist = True
            break

    if not exist:
        data.append(
            {
                'users': [owner, id],
                'messages': [messageObj]
            }
        )
    dumpData(data)

@blueprint.app_context_processor
def utility_processor():
    def getUnr():
        return getUnreads()
    return dict(getUnr=getUnr)
    
    
@blueprint.route('/api/messages/<int:id>', methods=['GET'])
@login_required
def getMes(id):
    try:
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.id == id).first() and current_user.id != id:
            messages = getMessages(id)
            return jsonify({
                'success': True,
                'messages': messages
            })
        else:
            raise Exception('user not found')
    except Exception as e:
        db_sess.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 401
    finally:
        db_sess.close()


@blueprint.route('/api/messages/<int:id>/send', methods=['POST'])
@login_required
def sendMes(id):
    try:
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.id == id).first() and current_user.id != id:
            payload: dict = request.get_json()
            content = payload.get('content')
            if not content:
                raise Exception('content field required')
            sendMessage(id, content)
            return jsonify({
                'success': True
            })
        else:
            raise Exception('user not found')
    except Exception as e:
        db_sess.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 401
    finally:
        db_sess.close()


@blueprint.route('/send_message/<int:id>', methods=['POST'])
def formSend(id):
    try:
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.id == id).first() and current_user.id != id:
            content = request.form.get('content')
            if not content:
                raise Exception('content field required')
            sendMessage(id, content)
            return redirect(f'/chat/{id}')
        else:
            raise Exception('user not found')
    except Exception as e:
        db_sess.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 401
    finally:
        db_sess.close()