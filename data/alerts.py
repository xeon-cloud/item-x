import datetime
import sqlalchemy
from . import db_session


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
        sqlalchemy.DateTime, default=datetime.datetime.now
    )