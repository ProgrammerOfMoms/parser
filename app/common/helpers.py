import os


def get_file_name_with_ext(file_path: str) -> tuple[str, str]:
    """
    Получить имя файла и его расширение.
    :param file_path: Путь до файла.
    """
    _, file_name = os.path.split(file_path)
    _, ext = os.path.splitext(file_name)
    return file_name, ext


def move_files_by_map(file_map: dict[str, str]) -> None:
    """
    Перенос файлов.
    :param file_map: Словарь, в котором
        ключи - текущие расположения файлов
        значение - куда требуется перенести
    """
    for source, destination in file_map.items():
        os.replace(source, destination)
