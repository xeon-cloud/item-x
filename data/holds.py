import sqlalchemy
import time
from . import db_session
from .users import User
from .alerts import Alert, RenderAlerts


class Hold(db_session.SqlAlchemyBase):
    __tablename__ = 'holds'

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True
    )
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer
    )
    amount = sqlalchemy.Column(
        sqlalchemy.Integer
    )
    end_date = sqlalchemy.Column(
        sqlalchemy.Integer, default=int(time.time())
    )

def targetHolds(id):
    with db_session.create_session() as sess:
        try:
            user = sess.query(User).filter(User.id == id).first()
            res = sess.query(Hold).filter(Hold.user_id == id).all()
            for i in res:
                if time.time() >= i.end_date:
                    sess.delete(i)
                    user.hold = user.hold - i.amount
                    user.balance += i.amount

                    render = RenderAlerts()
                    alert = render.unhold

                    sess.add(Alert(
                        owner=id,
                        header=alert[0],
                        content=alert[1].format(i.amount)
                    ))
            sess.commit()
        except Exception as e:
            sess.rollback()
            print(f'target ex. error: {e}')