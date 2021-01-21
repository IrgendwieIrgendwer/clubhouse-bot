from typing import Union

from PyDrocsid.database import db
from sqlalchemy import Column, Integer, String, BigInteger, Boolean


class Category(db.Base):
    __tablename__ = "category"

    category_id: Union[Column, int] = Column(BigInteger, primary_key=True, unique=True)

    @staticmethod
    def create(category_id: int) -> "Category":
        row = Category(category_id=category_id)
        db.add(row)
        return row
