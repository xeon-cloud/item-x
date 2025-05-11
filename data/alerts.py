import time
import sqlalchemy
from . import db_session

class RenderAlerts:
    purchase = (
        '<span class="ms-2"><i class="fa fa-credit-card" aria-hidden="true" style="margin-right: 5px"></i>Новая продажа</span>',
        '<a href="/user/{}" style="color: #00FFFF">{}</a> купил ваш товар <a href="/category/{}/{}/{}" style="color: #FFD700">{}</a>.<br><i class="fa fa-hourglass-start" aria-hidden="true" style="margin-right: 5px"></i><span style="color: #FFD700">{}₽ заморожены на 24 часа.</span>'
    )
    unhold = (
        '<span class="ms-2"><i class="fa fa-unlock-alt" aria-hidden="true" style="margin-right: 5px"></i>Холд окончен</span>',
        '<span style="color: #00FF00">{}₽ зачислены на ваш баланс</span>'
    )

class Alert(db_session.SqlAlchemyBase):
    __tablename__ = 'alerts'

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True
    )
    owner = sqlalchemy.Column(
        sqlalchemy.Integer
    )
    header = sqlalchemy.Column(
        sqlalchemy.String
    )
    content = sqlalchemy.Column(
        sqlalchemy.String
    )
    read = sqlalchemy.Column(
        sqlalchemy.Integer, default=0
    )
    created_date = sqlalchemy.Column(
        sqlalchemy.Integer, default=int(time.time())
    )