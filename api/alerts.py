from flask import Blueprint, jsonify
from flask_login import current_user
import datetime

from api.http_auth import auth

from data import db_session
from data.alerts import Alert

blueprint = Blueprint('alerts', __name__, template_folder='templates')

def format_timestamp(timestamp):
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    now = datetime.datetime.now()
    today = datetime.datetime(now.year, now.month, now.day)
    yesterday = today - datetime.timedelta(days=1)

    month_names_ru = {
        1: "Января", 2: "Февраля", 3: "Марта", 4: "Апреля", 5: "Мая", 6: "Июня",
        7: "Июля", 8: "Августа", 9: "Сентября", 10: "Октября", 11: "Ноября", 12: "Декабря"
    }

    if dt_object >= today:
        return "Сегодня в " + dt_object.strftime("%H:%M")
    elif dt_object >= yesterday:
        return "Вчера в " + dt_object.strftime("%H:%M")
    else:
        day = dt_object.day
        month = month_names_ru[dt_object.month]
        return f"{day} {month} в {dt_object.strftime('%H:%M')}"

@blueprint.app_context_processor
def utility_processor():
    def getAlerts():
        db_sess = db_session.create_session()
        res = db_sess.query(Alert).filter(Alert.owner == current_user.id or Alert.owner == 0).all()
        db_sess.close()
        unread = sum([1 for i in res if i.read == 0])
        return [
            '<hr class="my-1">'.join(list(reversed([f'<div class="notification-item p-2"><strong>{i.header}</strong><p style="margin-top: 7px;">{i.content}</p><i>{format_timestamp(i.created_date)}</i></div>' for i in res]))),
            unread
        ]
    return dict(getAlerts=getAlerts)


@blueprint.route('/api/alerts/read', methods=['POST'])
@auth.login_required
def readAlerts():
    db_sess = db_session.create_session()
    res = db_sess.query(Alert).filter(Alert.owner == auth.current_user().id and Alert.read == 0).all()
    for i in res:
        i.read = 1
    db_sess.commit()
    db_sess.close()
    return jsonify({'success': True})