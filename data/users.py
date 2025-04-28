import datetime
import sqlalchemy
from flask_login import UserMixin
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
    hashed_password = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )
    ya_id = sqlalchemy.Column(
        sqlalchemy.Integer, nullable=True
    )
    created_date = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.now
    )