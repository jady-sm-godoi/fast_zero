from http import HTTPStatus

from fastapi.testclient import TestClient

from app import app


def test_root_dev_retornar_ok_e_ola_mundo():
    client = TestClient(app) #Arrange
    response = client.get("/") #Act

    assert response.status_code == HTTPStatus.OK #Assert
    assert response.json() == {"message": "Olá mundo!"} #Assert
