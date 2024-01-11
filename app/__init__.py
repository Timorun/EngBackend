from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from definitions import OULAD_DATA_DIR

from lib_ml.data_utils.oulad_preprocessing import load_data

from .api.routes import student
from .auth.auth import auth_blueprint


def create_app():
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    # # Setup the Flask-JWT-Extended extension
    # app.config['JWT_ALGORITHM'] = 'RS256'
    #
    # # Load the private key with the passphrase
    # private_key_passphrase = 'your_passphrase_here'
    # private_key = open('rs256.pem').read()
    # app.config['JWT_PRIVATE_KEY'] = open('rs256.pem').read()
    # app.config['JWT_PUBLIC_KEY'] = open('rs256.pub').read()
    app.config['JWT_SECRET_KEY'] = 'RandomKeyTimothy0364'  # Change this to a random secret key!
    jwt = JWTManager(app)

    # Load and attach the dataset to the app object
    app.datasets = load_data(data_folder=OULAD_DATA_DIR)

    app.register_blueprint(student)
    app.register_blueprint(auth_blueprint)

    return app
