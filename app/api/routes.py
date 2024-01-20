from flask import Blueprint, request, jsonify
import pandas as pd
from flask import current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from lib_data.database import accesscheck

dataroute = Blueprint('student', __name__, url_prefix='/api')

# COURSE Data
# Returns the count of interactions per day.
@dataroute.route('/courseinteractions')
@jwt_required()
def get_courses_interactions():
    current_user = get_jwt_identity()

    module_code = request.args.get('module_code')
    presentation_code = request.args.get('presentation_code')

    # Date for now hardcoded for prototype purpose, simulating being in a course in progress
    # days = request.args.get('date')

    if not module_code or not presentation_code:
        return jsonify({"error": "Module code and presentation code are required"}), 400

    # Check if allowed to access using JWT token and accesstable
    access = accesscheck(current_app.cipher_suite, current_user, module_code, presentation_code)

    if access:
        studentvle = current_app.datasets['student_vle']
        studentvle = studentvle[studentvle['date'] < 132]

        # Filter for the specific student and module-presentation and date
        studentvle = studentvle[(studentvle['code_module'] == module_code) & (studentvle['code_presentation'] == presentation_code)]
        # Grouping the data by code_module, code_presentation, and date and calculating the total sum of clicks
        total_clicks_df = studentvle.groupby(['code_module', 'code_presentation', 'date'])[
            'sum_click'].sum().reset_index()
        # Renaming the sum_click column to total_clicks for clarity
        total_clicks_df.rename(columns={'sum_click': 'total_clicks'}, inplace=True)
        total_clicks_df = total_clicks_df[['date', 'total_clicks']]

        # Convert DataFrame to JSON
        interaction_data = total_clicks_df.to_dict(orient='records')
        return jsonify({
            "message": "Interaction counts",
            "interaction_data": interaction_data
        })
    else:
        return jsonify({"error": "Access to this module-presentation not allowed"}), 401



# STUDENT Data
# Returns list of student's within a specific course.
@dataroute.route('/studentids')
@jwt_required()
def get_student_ids():
    current_user = get_jwt_identity()

    module_code = request.args.get('module_code')
    presentation_code = request.args.get('presentation_code')

    if not module_code or not presentation_code:
        return jsonify({"error": "Module code and presentation code are required"}), 400

    # Check if allowed to access using JWT token and accesstable
    access = accesscheck(current_app.cipher_suite, current_user, module_code, presentation_code)

    if access:
        student_info = current_app.datasets['student_info']

        filtered_students = student_info[(student_info['code_module'] == module_code) &
                                         (student_info['code_presentation'] == presentation_code)]

        student_ids = filtered_students['id_student'].tolist()
        return jsonify({
            "message": "Student IDs found",
            "student_ids": student_ids
        })
    else:
        return jsonify({"error": "Access to this module-presentation not allowed"}), 401


# This function will return an individual student's assessment scores over time within a specific course.
@dataroute.route('/studentassessment')
@jwt_required()
def student_performance_trend():
    current_user = get_jwt_identity()

    student_id = int(request.args.get('student_id'))
    code_module = str(request.args.get('code_module'))
    code_presentation = str(request.args.get('code_presentation'))

    # Check if allowed to access using JWT token and accesstable
    access = accesscheck(current_app.cipher_suite, current_user, code_module, code_presentation)

    if access:
        assessments = current_app.datasets['assessments']
        studentassessment = current_app.datasets['student_assessment']

        # Merge student assessment data with assessment details
        merged_data = pd.merge(studentassessment, assessments, on='id_assessment')
        # Filter for the specific student and module-presentation
        student_data = merged_data[(merged_data['id_student'] == student_id) &
                                   (merged_data['code_module'] == code_module) &
                                   (merged_data['code_presentation'] == code_presentation)]

        # Select relevant columns
        performance_data = student_data[['id_assessment', 'assessment_type', 'date', 'score', 'weight']]
        # Convert DataFrame to JSON
        # performance_json = performance_data.to_json(orient='records')
        performance_data = performance_data.to_dict(orient='records')

        # Return JSON response
        return jsonify({
            "message": "Student assessments found",
            "student_assessments": performance_data
        })
    else:
        return jsonify({"error": "Access to this module-presentation not allowed"}), 401



# This function analyzes a student’s interaction with VLE materials over time within a specific module-presentation.
@dataroute.route('/studentinteractions')
@jwt_required()
def student_engagement_trend():
    current_user = get_jwt_identity()

    student_id = int(request.args.get('student_id'))
    code_module = str(request.args.get('code_module'))
    code_presentation = str(request.args.get('code_presentation'))

    # Date for now hardcoded for prototype purpose, simulating being in a course in progress
    # days = request.args.get('date')

    # Check if allowed to access using JWT token and accesstable
    access = accesscheck(current_app.cipher_suite, current_user, code_module, code_presentation)

    if access:
        studentvle = current_app.datasets['student_vle']
        studentvle = studentvle[studentvle['date'] < 132]

        # Filter for the specific student and module-presentation
        student_data = studentvle[(studentvle['id_student'] == student_id) &
                                  (studentvle['code_module'] == code_module) &
                                  (studentvle['code_presentation'] == code_presentation)]
        # Group by date and sum the interactions
        interaction_data = student_data.groupby('date')['sum_click'].sum().reset_index()

        # Convert DataFrame to JSON
        interaction_data = interaction_data.to_dict(orient='records')

        # Return JSON response
        return jsonify({
            "message": "Student interaction data",
            "student_interactions": interaction_data
        })
    else:
        return jsonify({"error": "Access to this module-presentation not allowed"}), 401


# This function checks if a student tends to submit assessments early, on time, or late within a specific module-presentation.
@dataroute.route('/submissions')
@jwt_required()
def assessment_submission_timeliness():
    current_user = get_jwt_identity()

    student_id = int(request.args.get('student_id'))
    code_module = str(request.args.get('code_module'))
    code_presentation = str(request.args.get('code_presentation'))

    # Check if allowed to access using JWT token and access table
    access = accesscheck(current_app.cipher_suite, current_user, code_module, code_presentation)

    if access:
        studentassessment = current_app.datasets['student_assessment']
        assessments = current_app.datasets['assessments']

        # Merge the dataframes
        merged_data = pd.merge(studentassessment, assessments, on='id_assessment')
        # Filter for the specific student and module-presentation
        student_data = merged_data[(merged_data['id_student'] == student_id) &
                                   (merged_data['code_module'] == code_module) &
                                   (merged_data['code_presentation'] == code_presentation)]
        # Calculate submission timeliness
        student_data['submission_timeliness'] = student_data['date_submitted'] - student_data['date']

        # Return JSON response
        return jsonify({
            "message": "Student submission data",
            "student_interactions": student_data[
                ['id_assessment', 'date_submitted', 'date', 'submission_timeliness']].to_dict(orient='records')
        })
    else:
        return jsonify({"error": "Access to this module-presentation not allowed"}), 401