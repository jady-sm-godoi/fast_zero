from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from schemas import Message

app = FastAPI()


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Olá mundo!"}


@app.get("/exercicio-html", response_class=HTMLResponse)
def exercicio_aula_02():
    return """
    <html>
        <head>
            <title>Exercício Aula 02</title>
        </head>
        <body>
            <h1>Exercício Aula 02</h1>
            <p>Este é um exemplo de resposta HTML.</p>
        </body>
    </html>
    """
