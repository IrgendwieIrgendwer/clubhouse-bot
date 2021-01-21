from datetime import datetime
from typing import Union

from PyDrocsid.database import db
from sqlalchemy import Column, Integer, BigInteger, DateTime, Enum

from models.state import State


class Donator(db.Base):
    __tablename__ = "donator"

    user_id: Union[Column, int] = Column(BigInteger, primary_key=True, unique=True)
    invite_count: Union[Column, int] = Column(Integer)
    used_invites: Union[Column, int] = Column(Integer)
    last_contact: Union[Column, datetime] = Column(DateTime)
    state: Union[Column, State] = Column('state', Enum(State))

    @staticmethod
    def create(user_id: int, last_contact: DateTime = datetime.utcnow()) -> "Donator":
        row = Donator(user_id=user_id, last_contact=last_contact, used_invites=0, invite_count=0, state=State.INITIAL)
        db.add(row)
        return row

    @staticmethod
    def change_invite_count(user_id: int, invite_count: int):
        row: Donator = db.get(Donator, user_id)
        row.invite_count = invite_count

    @staticmethod
    def change_used_invites(user_id: int, used_invites: int):
        row: Donator = db.get(Donator, user_id)
        row.used_invites = used_invites

    @staticmethod
    def change_state(user_id: int, state: State):
        row: Donator = db.get(Donator, user_id)
        row.state = state

    @staticmethod
    def change_last_contact(user_id: int, last_contact: DateTime):
        row: Donator = db.get(Donator, user_id)
        row.last_contact = last_contact
