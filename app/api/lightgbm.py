from flask import Blueprint, request, jsonify
import pandas as pd
from flask import current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from lib_ml.ml_utils.lgbm2 import generate_predictions

lgbmblueprint = Blueprint('lgbm', __name__, url_prefix='/api')



# Returns list of student's predicted final results
@lgbmblueprint.route('/predict', methods=['POST'])
@jwt_required()
def get_predicted_result():
    current_user = get_jwt_identity()
    print(current_user)

    # Get student_id_list from request body
    student_id_list = request.json.get('student_ids')
    # print(student_id_list)

    # Add sending date of module
    days = 132

    predictions = generate_predictions(days, student_id_list)

    return jsonify({
        "message": "Final result predictions",
        "student_ids": predictions.tolist()
    })





