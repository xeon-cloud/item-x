import sqlalchemy
import time
from . import db_session

class Review(db_session.SqlAlchemyBase):
    __tablename__ = 'reviews'

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True
    )
    owner = sqlalchemy.Column(
        sqlalchemy.Integer, nullable=False
    )
    seller = sqlalchemy.Column(
        sqlalchemy.Integer, nullable=False
    )
    date = sqlalchemy.Column(
        sqlalchemy.Integer, default=int(time.time())
    )