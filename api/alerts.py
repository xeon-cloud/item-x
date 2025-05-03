from flask import Blueprint, jsonify
from data import db_session
from data.alerts import Alert
from flask_login import current_user, login_required

blueprint = Blueprint('alerts', __name__, template_folder='templates')

@blueprint.app_context_processor
def utility_processor():
    def getAlerts():
        db_sess = db_session.create_session()
        res = db_sess.query(Alert).filter(Alert.owner == current_user.id).all()
        db_sess.close()
        unread = sum([1 for i in res if i.read == 0])
        return [
            '<hr class="my-1">'.join(list(reversed([f'<div class="notification-item p-2"><strong>{i.header}</strong><p>{i.content}</p></div>' for i in res]))),
            unread
        ]
    return dict(getAlerts=getAlerts)


@blueprint.route('/api/alerts/read', methods=['POST'])
@login_required
def readAlerts():
    db_sess = db_session.create_session()
    res = db_sess.query(Alert).filter(Alert.owner == current_user.id and Alert.read == 0).all()
    for i in res:
        i.read = 1
    db_sess.commit()
    db_sess.close()
    return jsonify({'success': True})