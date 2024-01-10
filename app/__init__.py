from flask import Flask
from flask_cors import CORS
from definitions import OULAD_DATA_DIR
from .api.routes import student
from lib_ml.data_utils.oulad_preprocessing import load_data


def create_app():
    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    # Load and attach the dataset to the app object
    app.datasets = load_data(data_folder=OULAD_DATA_DIR)

    app.register_blueprint(student)

    return app
