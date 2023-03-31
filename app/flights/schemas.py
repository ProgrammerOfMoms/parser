from datetime import date
from pydantic import BaseModel, Field, validator


FILE_NAME_PATTERN = "^[0-9]{4}[0-9]{2}[0-9]{2}_.+[0-9]_.+\\.csv"


class FlightBase(BaseModel):
    """Базовая схема таблицы flights"""
    class Config:
        orm_mode = True


class FlightIn(FlightBase):
    """Входящая схема таблицы flights."""
    file_name: str = Field(description="Наименование входящего файла",
                           pattern=FILE_NAME_PATTERN)
    flt: int = Field(description="Номер рейса", gt=0)
    depdate: date = Field(description="Дата рейса в формате YYYY-MM-DD")
    dep: str = Field(description="Аэропорт вылета")

    @validator("file_name")
    def validate_flight_date(cls, file_name: str) -> str:
        """Валидация на дату полета из названия входящего файла."""
        year = int(file_name[:4])
        month = int(file_name[4:6])
        day = int(file_name[6:8])
        file_date = date(year, month, day)
        if not date(1970, 1, 1) <= file_date <= date.today():
            raise ValueError("Must be valid range")
        return file_name


class FlightOut(FlightIn):
    """Исходящая схема таблицы flights"""
    id: int = Field(description="Номер рейса", gt=0)
