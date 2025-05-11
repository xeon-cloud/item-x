import time
import datetime
import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db_session


class User(db_session.SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True
    )
    username = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )
    email = sqlalchemy.Column(
        sqlalchemy.String, index=True, unique=True, nullable=True
    )
    balance = sqlalchemy.Column(
        sqlalchemy.Integer, default=0
    )
    hold = sqlalchemy.Column(
        sqlalchemy.Integer, default=0
    )
    hashed_password = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )
    ya_id = sqlalchemy.Column(
        sqlalchemy.Integer, nullable=True
    )
    avatar = sqlalchemy.Column(
        sqlalchemy.Integer, default=0
    )
    good_reviews = sqlalchemy.Column(
        sqlalchemy.Integer, default=0
    )
    bad_reviews = sqlalchemy.Column(
        sqlalchemy.Integer, default=0
    )
    avatar = sqlalchemy.Column(
        sqlalchemy.Integer, default=0
    )
    created_date = sqlalchemy.Column(
        sqlalchemy.Integer, default=int(time.time())
    )
    last_activity = sqlalchemy.Column(
        sqlalchemy.Integer, default=int(time.time())
    )

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
    
    def format_date(self):
        months = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня',
                  'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря']

        date = datetime.datetime.fromtimestamp(self.created_date)
        return f'{date.day} {months[date.month - 1]} {date.year}'
    
    def format_activity(self):
        diff = int(time.time()) - self.last_activity
        if diff < 60:
            return '<span class="online">В сети</span>', 1
        elif diff < 3600:
            minutes = diff // 60
            ends = {
                '1': 'y',
                '2, 3, 4': 'ы',
                '5, 6, 7, 8, 9, 0': ''
            }
            for i, j in ends.items():
                if str(minutes)[-1] in i.split(', '):
                    end =  j
                    break
            return f'<span class="last-activity offline">Был(а) {minutes} минут{end} назад</span>', 0
        elif diff < 86400:
            return f'<span class="last-activity offline">Был(а) {diff // 3600} часов назад</span>', 0
        else:
            return f'<span class="last-activity offline">Был(а) {diff // 86400} дней назад</span>', 0