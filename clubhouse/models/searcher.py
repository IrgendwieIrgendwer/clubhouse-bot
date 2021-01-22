from datetime import datetime
from typing import Union

from PyDrocsid.database import db
from sqlalchemy import Column, BigInteger, Enum, DateTime

from models.state import State


class Searcher(db.Base):
    __tablename__ = "searcher"

    user_id: Union[Column, int] = Column(BigInteger, primary_key=True, unique=True)
    state: Union[Column, State] = Column('state', Enum(State))
    enqueued_at: Union[Column, datetime] = Column(DateTime)

    @staticmethod
    def create(user_id: int, enqueued_at: DateTime = datetime.utcnow()) -> "Searcher":
        row = Searcher(user_id=user_id, state=State.INITIAL, enqueued_at=enqueued_at)
        db.add(row)
        return row

    @staticmethod
    def change_state(user_id: int, state: State):
        row: Searcher = db.get(Searcher, user_id)
        row.state = state

    @staticmethod
    def set_timestamp(user_id: int):
        row: Searcher = db.get(Searcher, user_id)
        row.enqueued_at = datetime.utcnow()
