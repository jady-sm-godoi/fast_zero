from dataclasses import asdict

from sqlalchemy import select

from models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username="jady", password="secret", email="jady@teste.com"
        )
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == "jady"))

    assert asdict(user) == {
        "id": 1,
        "username": "jady",
        "password": "secret",
        "email": "jady@teste.com",
        "created_at": time,
    }
