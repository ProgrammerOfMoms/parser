from abc import ABC, abstractmethod
import csv
import json
from typing import TextIO


class BaseConvertor(ABC):
    """Базовый класс преобразователя"""

    def __init__(self, input_file_path: str,
                 output_file_path: str = "") -> None:
        """
        Конструктор.
        :param input_file_path: Путь до файла который нужно конвертировать
        """
        self._input_file_path = input_file_path
        self._output_file_path = output_file_path

    @abstractmethod
    def _convert(self, input_file: TextIO) -> str:
        """
        Реализация конвертации файла.
        :param input_file: Входящий файл.
        """

    def save(self, converted_data: str) -> None:
        """Сохранить ковертированный файл"""
        with open(self._output_file_path, "w",
                  encoding="utf-8") as output_file:
            output_file.write(converted_data)

    def convert(self) -> str:
        """Ковертировать входящий файл"""
        with open(self._input_file_path, encoding="utf-8") as input_file:
            converted_data = self._convert(input_file)
        if self._output_file_path:
            self.save(converted_data)
        return converted_data


class CsvToJsonConvertor(BaseConvertor):
    """Преобразователь из csv в JSON"""
    def __init__(self, input_file_path: str,
                 output_file_path: str = "") -> None:
        """
        Конструктор.
        :param input_file_path: Путь до файла который нужно конвертировать
        """
        super().__init__(input_file_path, output_file_path)
        self._json_data: list | None = None

    @property
    def json_data(self) -> list:
        """Получить JSON данные файла"""
        return self._json_data or []

    def _transform_row(self, row: dict) -> dict:
        """
        Преобразование строки.
        :param row: Строка файла, приведенная к словарю.
        """
        return row

    def _convert(self, input_file: TextIO) -> str:
        """
        Реализация конвертации файла.
        :param input_file: Входящий файл.
        """
        csv_reader = csv.DictReader(input_file, delimiter=";")
        self._json_data = [self._transform_row(row) for row in csv_reader]
        return json.dumps(self._json_data)
