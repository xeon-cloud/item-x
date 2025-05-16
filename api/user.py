from flask import Blueprint, jsonify

from api.http_auth import auth
from data.users import User


blueprint = Blueprint('user', __name__, template_folder='templates')

def renderUserResponse(user: User):
    return {
        'id': user.id,
        'username': user.username,
        'wallet': {
            'total': user.balance,
            'hold': user.hold
        }
    }

@blueprint.route('/api/users/me', methods=['GET'])
@auth.login_required
def getUserInfo():
    """Получение информации о себе"""
    try:
        return jsonify({
            'success': True,
            'data': renderUserResponse(auth.current_user())
        })
    except Exception as e:
        print(f'user api err - {e}')
        return jsonify({
            'success': False,
            'message': str(e)
        }), 403