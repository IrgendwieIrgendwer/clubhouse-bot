from typing import Union

from PyDrocsid.database import db
from sqlalchemy import Column, BigInteger, Enum

from models.state import State


class Searcher(db.Base):
    __tablename__ = "searcher"

    user_id: Union[Column, int] = Column(BigInteger, primary_key=True, unique=True)
    state: Union[Column, State] = Column('state', Enum(State))

    @staticmethod
    def create(user_id: int) -> "Searcher":
        row = Searcher(user_id=user_id, state=State.INITIAL)
        db.add(row)
        return row

    @staticmethod
    def change_state(user_id: int, state: State):
        row: Searcher = db.get(Searcher, user_id)
        row.state = state
