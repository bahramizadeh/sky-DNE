import pytest
from unittest.mock import patch
from resources.user import UserRegister, User, Login, UserLogout, TokenRefresh
from models.user import UserModel


@patch("resources.user.db")
@patch("resources.user.UserModel")
def test_user_register(mock_um, db):
    user_info = {"username": "admin", "password": "testpassword"}
    mock_um.query.filter(
        UserModel.username == user_info["username"]
    ).first.return_value = None
    user_register = UserRegister()
    user_register._post(user_info)


@patch("resources.user.db")
@patch("resources.user.UserModel")
def test_user_register_abort(mock_um, db):
    user_info = {"username": "admin", "password": "testpassword"}

    user = UserModel(**user_info)
    mock_um.query.filter(
        UserModel.username == user_info["username"]
    ).first.return_value = user
    user_register = UserRegister()
    with pytest.raises(Exception):
        user_register._post(user_info)


@patch("resources.user.UserModel")
def test_user_get(mock_um):
    user_id = 1
    user_info = {"username": "admin", "password": "testpassword"}
    user = UserModel(**user_info)
    mock_um.query.get_or_404(user_id).return_value = user
    user_instance = User()
    user_instance._get(user_id)


@patch("resources.user.db")
@patch("resources.user.UserModel")
@patch("resources.user.get_jwt")
def test_user_delete(mock_jwt, mock_um, db):

    user_id = 2
    user_info = {"username": "admin", "password": "testpassword"}
    mock_um.query.get_or_404(user_id).return_value = user_info
    user_instance = User()
    user_instance._delete(user_id)


@patch("resources.user.pbkdf2_sha256.verify")
@patch("resources.user.create_refresh_token")
@patch("resources.user.create_access_token")
@patch("resources.user.UserModel")
def test_login(mock_um, mock_at, mock_rt, mock_pbk):

    user_info = {"username": "admin", "password": "testpassword"}

    access_tocken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6dHJ1ZSwiaWF0IjoxNjkwMzY4NjY4LCJqdGkiOiJkNDZjZjI0Yy0yMTkxLTQwODktOWI4YS05YzMwYjAwOTQwMTEiLCJ0eXBlIjoiYWNjZXNzIiwic3ViIjoyLCJuYmYiOjE2OTAzNjg2NjgsImV4cCI6MTY5MDM2OTU2OCwiaXNfYWRtaW4iOmZhbHNlfQ.Lr_P43-2E7AaYs_m_9OVE1Rgo6t0BsvFgVylbHQrtrU"
    refresh_tocken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY5MDM2ODY2OCwianRpIjoiYTUzZjMzNjAtNDUxNC00YzhmLTg2M2QtMjdlM2IzMjBhOGQ0IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOjIsIm5iZiI6MTY5MDM2ODY2OCwiZXhwIjoxNjkyOTYwNjY4LCJpc19hZG1pbiI6ZmFsc2V9.621ZbqLTZutH_yalpy0ReoL_3RPc-anwzN70Q2-0aTE"

    user = UserModel(**user_info)
    mock_um.query.filter(
        UserModel.username == user_info["username"]
    ).first.return_value == user

    mock_at.return_value = access_tocken
    mock_rt.return_value = refresh_tocken
    mock_pbk.return_value = user_info["password"]
    login = Login()
    login._post(user_info)


@patch("resources.user.pbkdf2_sha256.verify")
@patch("resources.user.UserModel")
def test_login_abort(mock_um, mock_pbk):

    user_info = {"username": "admin", "password": "testpassword"}

    mock_um.query.filter(
        UserModel.username == user_info["username"]
    ).first.return_value == None

    mock_pbk.return_value = None
    login = Login()
    with pytest.raises(Exception):
        login._post(user_info)


@patch("resources.user.get_jwt")
def test_logout(mock_jwt):

    user_logout = UserLogout()
    user_logout._post()


@patch("resources.user.create_access_token")
@patch("resources.user.get_jwt")
@patch("resources.user.get_jwt_identity")
def test_token_refresh(mock_id, mock_jwt, mock_at):

    identity = 1
    new_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY5MDM2ODY2OCwianRpIjoiYTUzZjMzNjAtNDUxNC00YzhmLTg2M2QtMjdlM2IzMjBhOGQ0IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOjIsIm5iZiI6MTY5MDM2ODY2OCwiZXhwIjoxNjkyOTYwNjY4LCJpc19hZG1pbiI6ZmFsc2V9.621ZbqLTZutH_yalpy0ReoL_3RPc-anwzN70Q2-0aTE"

    mock_id.return_value = identity
    mock_at.return_value = new_token

    token_refresh = TokenRefresh()
    token_refresh._post()
