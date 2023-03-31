from sqlalchemy import Column, Date, Integer, String

from app.db import Base


class Flight(Base):
    """Представление таблицы перелетов."""
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    flt = Column(Integer, nullable=False)
    depdate = Column(Date, nullable=False)
    dep = Column(String, nullable=False)
