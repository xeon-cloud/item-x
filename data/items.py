import sqlalchemy
import time
from . import db_session

class Item(db_session.SqlAlchemyBase):
    __tablename__ = 'items'

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True
    )
    name = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )
    about = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )
    content = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )
    file = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )
    owner = sqlalchemy.Column(
        sqlalchemy.Integer
    )
    category_name = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )
    subcategory_id = sqlalchemy.Column(
        sqlalchemy.Integer
    )
    amount = sqlalchemy.Column(
        sqlalchemy.Integer
    )
    buyer = sqlalchemy.Column(
        sqlalchemy.Integer
    )
    created_date = sqlalchemy.Column(
        sqlalchemy.Integer, default=int(time.time())
    )