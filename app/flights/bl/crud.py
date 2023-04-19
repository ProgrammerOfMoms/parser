"""CRUD методы для работы с моделью авиаперелетов Flights"""
import logging
from datetime import date
from typing import Sequence

from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from app.flights.models import Flight
from app.flights.schemas import FlightIn
from app.logging import logged

logger = logging.getLogger(__name__)


@logged
def create_flight(session: Session, flight: FlightIn) -> Flight:
    """
    Создать новую запись в таблице flights.
    :param flight: Объект авиаперелета.
    """
    new_flight = Flight(**flight.dict(exclude={"prl"}))
    session.add(new_flight)
    return new_flight


@logged
def get_flights(session: Session,
                date: date | None = None) -> list[Flight]:
    """
    Получить данные о перелетах
    :param date: Фильтрация по дате.
    """
    query = select(Flight)
    if date is not None:
        query = query.where(Flight.depdate == date)
    return list(session.execute(query).scalars())


@logged
def create_flights_bulk(session: Session,
                        flights: Sequence[FlightIn]) -> None:
    flights_dict = [{**flight.dict(exclude={"prl"})}
                    for flight in flights]
    session.execute(insert(Flight), flights_dict)
