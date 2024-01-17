from flask.testing import FlaskClient
import pytest
from app import create_app


@pytest.fixture(scope="module")
def client():
    db_uri = "sqlite:///test.db"
    app, jwt, db = create_app(__name__, db_uri)

    with app.app_context():
        db.create_all()

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_user_register_succeed(client: FlaskClient):
    new_user = {"username": "maryam", "password": "pass4rd"}

    endpoint = "/register"
    response = client.post(endpoint, json=new_user)

    result = response.json
    expected_result = {"message": "User created successfully."}
    assert response.status_code == 201
    assert result == expected_result


def test_duplicate_user(client: FlaskClient):
    new_user = {"username": "maryam", "password": "pass4rd"}

    endpoint = "/register"
    response = client.post(endpoint, json=new_user)
    assert response.status_code == 409


def test_wrong_user_payload(client: FlaskClient):
    new_user = {
        "username": "user4",
    }

    endpoint = "/register"
    response = client.post(endpoint, json=new_user)
    assert response.status_code == 422


def test_get_user_succeeded(client: FlaskClient):
    user_id = 1
    expected_result = {"id": 1, "username": "maryam"}

    endpoint = f"/user/{user_id}"
    response = client.get(endpoint)

    assert response.status_code == 200
    assert response.json == expected_result


def test_get_user_unsucceeded(client: FlaskClient):
    user_id = 10

    endpoint = f"/user/{user_id}"
    response = client.get(endpoint)
    assert response.status_code == 404


def test_delete_user_404(client: FlaskClient):

    user_id = 10

    endpoint = f"/user/{user_id}"
    response = client.delete(endpoint)
    assert response.status_code == 404


def test_delete_user_succeeded(client: FlaskClient):
    user_id = 1

    endpoint2 = f"/user/{user_id}"
    delete_response = client.delete(endpoint2)
    assert delete_response.status_code == 201
