import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from lib_data.database import find_user_by_email, check_password

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')


@auth_blueprint.route('/login', methods=['POST'])
def login():
    if request.method == "POST":
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        print(email, password)

        expiry = datetime.timedelta(minutes=60)

        user = find_user_by_email(email)
        if user is not None:
            if user and check_password(password, user['hashed_password']):
                access_token = create_access_token(identity=user['user_id'], expires_delta=expiry)
                return jsonify(access_token=access_token)

        return jsonify({"msg": "Bad email or password"}), 401
