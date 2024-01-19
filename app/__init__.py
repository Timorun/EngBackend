import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from definitions import OULAD_DATA_DIR, SQL_DIR

from lib_ml.data_utils.oulad_preprocessing import load_data
from .api.lightgbm import lgbmblueprint

from .api.routes import student
from .api.courseaccess import courseblueprint
from .auth.auth import auth_blueprint


def create_app():
    app = Flask(__name__)
    # app.config['CORS_HEADERS'] = 'Content-Type'
    CORS(app)

    app.config['JWT_SECRET_KEY'] = 'RandomKeyTimothy0364'  # random secret key
    jwt = JWTManager(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///'+os.path.join(SQL_DIR, 'database.db'))
    app.db = SQLAlchemy(app)

    # Load and attach the dataset to the app object
    app.datasets = load_data(data_folder=OULAD_DATA_DIR)

    app.register_blueprint(student)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(courseblueprint)
    app.register_blueprint(lgbmblueprint)

    return app

