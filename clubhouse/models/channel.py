from typing import Union

from PyDrocsid.database import db
from sqlalchemy import Column, BigInteger


class Channel(db.Base):
    __tablename__ = "channel"

    channel_id: Union[Column, int] = Column(BigInteger, primary_key=True, unique=True)
    # TODO use foreign keys
    searcher_id: Union[Column, int] = Column(BigInteger)
    # searcher_id = Column('searcher', Integer, ForeignKey('searcher.id'), nullable=False)
    # searcher = db.relationship('Channel', backref=db.backref('searcher', lazy=True))

    donator_id: Union[Column, int] = Column(BigInteger)
    # donator_id = Column('donator', Integer, ForeignKey('donator.id'), nullable=False)
    # donator = db.relationship('Channel', backref=db.backref('donator', lazy=True))

    @staticmethod
    def create(channel_id: int, donator_id: int, searcher_id: int) -> "Channel":
        row = Channel(channel_id=channel_id, donator_id=donator_id, searcher_id=searcher_id)
        db.add(row)
        return row
