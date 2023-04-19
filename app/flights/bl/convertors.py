from datetime import datetime

from app.common.convertors import CsvToJsonConvertor
from app.consts import DEFAULT_DATE_FORMAT


class CsvToJsonFlightConvertor(CsvToJsonConvertor):
    """Преобразователь из csv в JSON для файлов перелетов"""

    def _transform_row(self, row: dict) -> dict:
        """
        Преобразование строки.
        :param row: Строка файла, приведенная к словарю.
        """
        row = super()._transform_row(row)
        bdate = row.get("bdate", "")
        bdate = datetime.strptime(bdate.lower(), "%d%b%y")
        row["bdate"] = bdate.strftime(DEFAULT_DATE_FORMAT)
        return row
