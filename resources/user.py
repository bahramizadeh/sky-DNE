from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    jwt_required,
    create_refresh_token,
    get_jwt_identity,
)
from db import db

from models.user import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST


blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_info):
        return self._post(user_info)

    def _post(self, user_info):

        if UserModel.query.filter(UserModel.username == user_info["username"]).first():
            abort(409, message="A user with that username already exists.")

        user = UserModel(
            username=user_info["username"],
            password=pbkdf2_sha256.hash(user_info["password"]),
        )

        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        return self._get(user_id)

    def _get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @jwt_required(refresh=True)
    def delete(self, user_id):
        return self._delete(user_id)

    def _delete(self, user_id):

        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return {"message": "User deleted."}, 201


@blp.route("/login")
class Login(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_info):
        return self._post(user_info)

    def _post(self, user_info):
        user = UserModel.query.filter(
            UserModel.username == user_info["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_info["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)

            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        abort(401, message="Invalid credentials.")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        return self._post()

    def _post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)

        return {"message": "successfully logged out."}, 200


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):

        return self._post()

    def _post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)

        return {"access_token": new_token}, 200
