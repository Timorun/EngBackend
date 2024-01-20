from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from cryptography.fernet import Fernet

from definitions import OULAD_DATA_DIR

from lib_ml.data_utils.oulad_preprocessing import load_data
from lib_data.create import createcredentials, createaccess
from .api.lgbmroute import lgbmblueprint
from .api.routes import dataroute
from .api.courseaccess import courseblueprint
from .auth.auth import auth_blueprint


def create_app():
    app = Flask(__name__)
    # app.config['CORS_HEADERS'] = 'Content-Type'
    CORS(app)

    app.config['JWT_SECRET_KEY'] = 'RandomKeyTimothy0364'  # random secret key
    jwt = JWTManager(app)

    # Generate a key
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    app.cipher_suite = cipher_suite

    # Load and attach the OULAD dataset to the app object
    datasets = load_data(data_folder=OULAD_DATA_DIR)
    app.datasets = datasets

    # Initialize and encrypt credentials and access tables
    createcredentials(app.cipher_suite)
    createaccess(app.cipher_suite)

    app.register_blueprint(dataroute)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(courseblueprint)
    app.register_blueprint(lgbmblueprint)

    return app
