from fastapi.testclient import TestClient


def delete_id_field(json_data: list) -> list:
    for data in json_data:
        data.pop("id")


def test_create_flight(client: TestClient) -> None:
    """Тестирование эндпоинта создания авиаперелета"""
    data = {
        "file_name": "20221010_1234_DME.csv",
        "flt": 1234,
        "depdate": "2022-10-10",
        "dep": "DME"
    }
    response = client.post("/flights/", json=data)
    json_response = response.json()
    json_response.pop("id")
    assert response.status_code == 200
    assert json_response == data


def test_read_flights(client: TestClient) -> None:
    """Тестирование получения данных о полетах"""
    # пустая таблица
    response = client.get("/flights/")
    assert response.status_code == 200
    assert response.json() == []

    data = {
        "file_name": "20221010_1234_DME.csv",
        "flt": 1234,
        "depdate": "2022-10-10",
        "dep": "DME"
    }
    client.post("/flights/", json=data)
    response = client.get("/flights/")
    json_response = response.json()
    delete_id_field(json_response)
    assert response.status_code == 200
    assert json_response == [data]


def test_read_flights_with_date(client: TestClient) -> None:
    """
    Тестирование получения данных о полетах
    с фильтрацией по дате
    """
    data = [
        {
            "file_name": "20221010_1234_DME.csv",
            "flt": 1234,
            "depdate": "2022-10-10",
            "dep": "DME"
        },
        {
            "file_name": "20221010_1235_DME.csv",
            "flt": 1235,
            "depdate": "2022-10-10",
            "dep": "DME"
        },
        {
            "file_name": "20221011_1235_DME.csv",
            "flt": 1235,
            "depdate": "2022-10-11",
            "dep": "DME"
        }
    ]
    for flight in data:
        client.post("/flights/", json=flight)
    response = client.get("/flights/", params={"date": "2022-10-10"})
    json_response = response.json()
    delete_id_field(json_response)
    assert response.status_code == 200
    assert json_response == [data[0], data[1]]

    response = client.get("/flights/", params={"date": "2022-10-11"})
    json_response = response.json()
    delete_id_field(json_response)
    assert response.status_code == 200
    assert json_response == [data[2]]

    response = client.get("/flights/", params={"date": "2022-10-12"})
    json_response = response.json()
    delete_id_field(json_response)
    assert response.status_code == 200
    assert json_response == []
