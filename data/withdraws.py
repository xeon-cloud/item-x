import sqlalchemy
import time
import datetime
from . import db_session

class WithDraw(db_session.SqlAlchemyBase):
    __tablename__ = 'withdraws'

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True
    )
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer, nullable=False
    )
    amount = sqlalchemy.Column(
        sqlalchemy.Integer, nullable=False
    )
    reqs = sqlalchemy.Column(
        sqlalchemy.String, nullable=False
    )
    date = sqlalchemy.Column(
        sqlalchemy.Integer, default=int(time.time())
    )

    def format_date(self):
        months = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня',
                  'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря']

        date = datetime.datetime.fromtimestamp(self.date)
        return f'{date.day} {months[date.month - 1]} {date.year}'