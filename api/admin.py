from flask import Blueprint, request, jsonify, abort
from flask_login import login_required, current_user
from data import db_session
from data.users import User
from data.holds import Hold
from api.chats import sendMessage
import json
import os

blueprint = Blueprint('admin', __name__)

BANNED_USERS_FILE = 'banned_users.json'


def get_banned_users():
    try:
        with open(BANNED_USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []


def save_banned_users(data):
    with open(BANNED_USERS_FILE, 'w') as f:
        json.dump(data, f, indent=4)


@blueprint.route('/api/admin/search', methods=['GET'])
@login_required
def admin_search():
    if current_user.id != 0:
        abort(403)

    query = request.args.get('query', '').strip()
    db_sess = db_session.create_session()

    try:
        user = db_sess.query(User).filter(
            (User.id == query) |
            (User.username.ilike(f'%{query}%'))
        ).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'id': user.id,
            'username': user.username,
            'balance': user.balance,
            'hold': user.hold,
            'banned': str(user.id) in get_banned_users(),
            'reg_date': user.format_date(),
            'avatar': f'/static/images/avatars/{user.id if user.avatar == 1 else "default"}.png'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db_sess.close()


@blueprint.route('/api/admin/set_balance', methods=['POST'])
@login_required
def set_balance():
    if current_user.id != 0:
        abort(403)

    data = request.get_json()
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(data['user_id'])
    user.balance = data['balance']
    db_sess.commit()
    return jsonify({'success': True})


@blueprint.route('/api/admin/clear_holds', methods=['POST'])
@login_required
def clear_holds():
    if current_user.id != 0:
        abort(403)

    data = request.get_json()
    db_sess = db_session.create_session()
    db_sess.query(Hold).filter_by(user_id=data['user_id']).delete()
    user = db_sess.query(User).get(data['user_id'])
    user.hold = 0
    db_sess.commit()
    return jsonify({'success': True})


@blueprint.route('/api/admin/send_message', methods=['POST'])
@login_required
def send_message():
    if current_user.id != 0:
        abort(403)

    data = request.get_json()
    sendMessage(data['user_id'], data['content'], as_support=True)
    return jsonify({'success': True})


@blueprint.route('/api/admin/ban', methods=['POST'])
@login_required
def ban_user():
    if current_user.id != 0:
        abort(403)

    data = request.get_json()
    banned = get_banned_users()
    if data['user_id'] not in banned:
        banned.append(data['user_id'])
        save_banned_users(banned)
    return jsonify({'success': True})


@blueprint.route('/api/admin/unban', methods=['POST'])
@login_required
def unban_user():
    if current_user.id != 0:
        abort(403)

    data = request.get_json()
    banned = get_banned_users()
    if data['user_id'] in banned:
        banned.remove(data['user_id'])
        save_banned_users(banned)
    return jsonify({'success': True})