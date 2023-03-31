import logging

from fastapi import FastAPI

from app.flights.routers import router as flights_router
from app.logging import setup_logger
from app.middleware import log_requests


setup_logger()
logger = logging.getLogger(__name__)


app = FastAPI(title="S7 IT Test",
              description="API для работы с данными авиакомпании.")
app.middleware("http")(log_requests)
app.include_router(flights_router,
                   prefix="/flights",
                   tags=["flights"])
