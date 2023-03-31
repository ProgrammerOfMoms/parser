from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.flights.schemas import FlightIn, FlightOut
from app.flights.bl import crud

router = APIRouter()


@router.get("/", tags=["flights"])
def read_flights(date: date | None = None,
                 session: Session = Depends(get_db)) -> list[FlightOut]:
    """Получить перелеты."""
    result = crud.get_flights(session, date)
    for res in result:
        print(type(res))
    return []


@router.post("/")
def create_flights(flight: FlightIn,
                   session: Session = Depends(get_db)) -> FlightOut:
    """Создать новый перелет."""
    return crud.create_flight(session, flight)
