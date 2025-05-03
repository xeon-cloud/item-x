from flask_httpauth import HTTPTokenAuth

from data import db_session
from data.users import User
import oauth.model as mod

auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(auth_token):
    try:
        user_id = mod.decodeAuthToken(auth_token)['id']
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        db_sess.close()
        if user:
            return user
    except Exception as e:
        print(f'HTTP Auth error - {e}')