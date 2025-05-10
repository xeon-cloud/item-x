import sqlalchemy
import time
import datetime
from . import db_session

class Purchase(db_session.SqlAlchemyBase):
    __tablename__ = 'purchases'

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True
    )
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False
    )
    item_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('items.id'), nullable=False
    )
    purchase_date = sqlalchemy.Column(
        sqlalchemy.Integer, default=int(time.time())
    )
    price = sqlalchemy.Column(
        sqlalchemy.Float, nullable=False
    )
    item_name = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )
    item_description = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )
    item_image = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )
    item_url = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )

    def format_date(self):
        months = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня',
                  'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря']

        date = datetime.datetime.fromtimestamp(self.purchase_date)
        return f'{date.day} {months[date.month - 1]} {date.year}'