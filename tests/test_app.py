from http import HTTPStatus

from fastapi.testclient import TestClient

from app import app


def test_root_dev_retornar_ok_e_ola_mundo():
    client = TestClient(app)  # Arrange
    response = client.get("/")  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {"message": "Olá mundo!"}  # Assert


def test_exercicio_aula_02_retornar_html():
    client = TestClient(app)  # Arrange
    response = client.get("/exercicio-html")  # Act

    assert response.status_code == HTTPStatus.OK  # Asserts
    assert "<h1>Exercício Aula 02</h1>" in response.text
    assert "<p>Este é um exemplo de resposta HTML.</p>" in response.text
