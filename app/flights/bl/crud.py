"""CRUD методы для работы с моделью авиаперелетов Flights"""
from datetime import date, datetime

import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.consts import DEFAULT_DATE_FORMAT
from app.flights.models import Flight
from app.flights.schemas import FlightIn
from app.logging import logged


logger = logging.getLogger(__name__)


@logged
def create_flight(session: Session,
                  flight: FlightIn,) -> Flight:
    """
    Создать новую запись в таблице flights.
    :param flight: Объект авиаперелета.
    """
    new_flight = Flight(**flight.dict())
    session.add(new_flight)
    session.commit()
    session.refresh(new_flight)
    return new_flight


@logged
def get_flights(session: Session,
                date: date | None = None) -> list[Flight]:
    query = select(Flight)
    if date is not None:
        date_filter = datetime.strftime(date, DEFAULT_DATE_FORMAT)
        query.where(Flight.depdate == date_filter)
    return session.execute(query).all()
