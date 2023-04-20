from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.flights.bl import crud
from app.flights.schemas import FlightIn, FlightOut

router = APIRouter()


@router.get("/", tags=["flights"])
def read_flights(date: date | None = None,
                 session: Session = Depends(get_db)) -> list[FlightOut]:
    """Получить перелеты."""
    return crud.get_flights(session, date)


@router.post("/")
def create_flights(flight: FlightIn,
                   session: Session = Depends(get_db)) -> FlightOut:
    """Создать новый перелет."""
    new_flight = crud.create_flight(session, flight)
    session.commit()
    return new_flight


@router.get("/ping")
def ping() -> str:
    return "pong"
