import sqlalchemy
from . import db_session


class SubCat(db_session.SqlAlchemyBase):
    __tablename__ = 'subcats'

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True
    )
    name = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )
    category = sqlalchemy.Column(
        sqlalchemy.String, nullable=True
    )