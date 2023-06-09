from datetime import date, datetime
import json
import os
from typing import TypeVar, Type, TypeAlias

from pydantic import BaseModel, Field, validator
from app.common.convertors import CsvToJsonConvertor
from app.consts import DEFAULT_DATE_FORMAT


DateType: TypeAlias = str | date

T = TypeVar('T', bound="FlightFullIn")

FILE_NAME_PATTERN = "^[0-9]{4}[0-9]{2}[0-9]{2}_.+[0-9]_.+\\.csv"


class Passenger(BaseModel):
    """Модель пассажира"""
    num: int
    surname: str
    firstname: str
    bdate: date

    @validator("bdate", pre=True)
    def validate_bdate(cls, bdate: str | date | None) -> date:
        """Валидация даты рождения"""
        if not isinstance(bdate, (str, date)):
            raise ValueError
        if isinstance(bdate, date):
            return bdate
        try:
            new_bdate = datetime.strptime(bdate.lower(), "%d%b%y")
        except ValueError:
            new_bdate = datetime.strptime(bdate, DEFAULT_DATE_FORMAT)
        return new_bdate.date()


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
            raise ValueError("Дата в названии файла должна быть в диапозоне"
                             "от 01-01-1970 до текущей даты.")
        return file_name

    @validator("depdate", pre=True)
    def validate_depdate(cls, depdate: DateType) -> date:
        """Валидация даты рождения"""
        if not isinstance(depdate, (str, date)):
            raise ValueError
        if isinstance(depdate, date):
            return depdate
        try:
            new_depdate = datetime.strptime(depdate.lower(), "%Y%m%d")
        except ValueError:
            new_depdate = datetime.strptime(depdate, DEFAULT_DATE_FORMAT)
        return new_depdate.date()

    def to_json(self,
                exclude: set[str] | None = None,
                replace: dict[str, str] | None = None) -> str:
        """
        Кастомный метод приведения объекта к JSON строке
        """
        json_str = self.json(exclude=exclude)
        if replace is None:
            return json_str
        dict_obj = json.loads(json_str)
        for old_key, new_key in replace.items():
            if old_key in dict_obj:
                dict_obj[new_key] = dict_obj.pop(old_key)
        return json.dumps(dict_obj)


class FlightOut(FlightIn):
    """Исходящая схема таблицы flights"""
    id: int = Field(description="Идентификатор полета", gt=0)


class FlightFullIn(FlightIn):
    """
    Модель с полными дынными о полете,
    включая информацию о пассажирах.
    """
    prl: list[Passenger] = Field(description="Список пассажиров")

    @classmethod
    def from_csv_file(cls: Type[T], csv_file_path: str) -> T:
        """
        Создает модель из csv файла.
        :param csv_file_path: Путь до csv файла.
        """
        _, file_name = os.path.split(csv_file_path)
        file_name_wo_ext, _ = os.path.splitext(file_name)
        date_str, flight_num, dep_name = file_name_wo_ext.split("_")
        convertor = CsvToJsonConvertor(csv_file_path)
        convertor.convert()
        return cls(
            file_name=file_name,
            flt=flight_num,
            depdate=date_str,
            dep=dep_name,
            prl=[Passenger(**passenger) for passenger in convertor.json_data]
        )
