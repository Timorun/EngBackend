import datetime
import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from definitions import DATABASE
from lib_data.database import find_user_by_email, check_password, hash_password, add_user_to_csv

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

        return jsonify({"msg": "Wrong email or password"}), 401


@auth_blueprint.route('/register', methods=['POST'])
def register():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if find_user_by_email(email):
        return jsonify({"msg": "Email already registered"}), 409

    next_user_id = sum(1 for _ in open(os.path.join(DATABASE, 'credentials.csv')))  # Naive way to generate a new user ID
    hashed_password = hash_password(password)
    add_user_to_csv(next_user_id, email, hashed_password)

    return jsonify({"msg": "User registered successfully"}), 201