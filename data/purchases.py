import sqlalchemy
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
        sqlalchemy.DateTime, default=datetime.datetime.now
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