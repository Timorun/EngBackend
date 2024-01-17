from flask import Blueprint, request, jsonify
import pandas as pd
from flask import current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

student = Blueprint('student', __name__, url_prefix='/api')


# Returns list of student's within a specific course.
@student.route('/studentids')
@jwt_required()
def get_student_ids():
    current_user = get_jwt_identity()
    print(current_user)

    module_code = request.args.get('module_code')
    presentation_code = request.args.get('presentation_code')

    if not module_code or not presentation_code:
        return jsonify({"error": "Module code and presentation code are required"}), 400

    student_info = current_app.datasets['student_info']

    filtered_students = student_info[(student_info['code_module'] == module_code) &
                                     (student_info['code_presentation'] == presentation_code)]

    student_ids = filtered_students['id_student'].tolist()

    return jsonify({
        "message": "Student IDs found",
        "student_ids": student_ids
    })


# Completed course analytics: #


# In progress course analytics: #


# This function will return an individual student's assessment scores over time within a specific course.
@student.route('/studentassessment')
@jwt_required()
def student_performance_trend():
    current_user = get_jwt_identity()
    print(current_user)

    student_id = int(request.args.get('student_id'))
    code_module = str(request.args.get('code_module'))
    code_presentation = str(request.args.get('code_presentation'))

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


# This function analyzes a student’s interaction with VLE materials over time within a specific module-presentation.
@student.route('/studentinteractions')
@jwt_required()
def student_engagement_trend():
    # current_user = get_jwt_identity()
    # print(current_user)

    student_id = int(request.args.get('student_id'))
    code_module = str(request.args.get('code_module'))
    code_presentation = str(request.args.get('code_presentation'))

    studentvle = current_app.datasets['student_vle']

    # Filter for the specific student and module-presentation
    student_data = studentvle[(studentvle['id_student'] == student_id) &
                              (studentvle['code_module'] == code_module) &
                              (studentvle['code_presentation'] == code_presentation)]
    # Group by date and sum the interactions
    interaction_data = student_data.groupby('date')['sum_click'].sum().reset_index()

    # Convert DataFrame to JSON
    # performance_json = performance_data.to_json(orient='records')
    interaction_data = interaction_data.to_dict(orient='records')

    # Return JSON response
    return jsonify({
        "message": "Student interaction data",
        "student_interactions": interaction_data
    })


# This function checks if a student tends to submit assessments early, on time, or late within a specific module-presentation.
@student.route('/submissions')
@jwt_required()
def assessment_submission_timeliness():
    student_id = int(request.args.get('student_id'))
    code_module = str(request.args.get('code_module'))
    code_presentation = str(request.args.get('code_presentation'))

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
        "student_interactions": student_data[['id_assessment', 'date_submitted', 'date', 'submission_timeliness']].to_dict(orient='records')
    })



# # This function compares an individual student’s performance with the average performance of the course within a specific module-presentation.
# def comparison_with_peers(student_id, code_module, code_presentation, assessments, studentassessment):
#     # Merge the dataframes
#     merged_data = pd.merge(studentassessment, assessments, on='id_assessment')
#     # Filter for the specific module-presentation
#     presentation_data = merged_data[(merged_data['code_module'] == code_module) &
#                                     (merged_data['code_presentation'] == code_presentation)]
#     # Calculate average scores for each assessment
#     avg_scores = presentation_data.groupby('id_assessment')['score'].mean().reset_index()
#     avg_scores.rename(columns={'score': 'avg_score'}, inplace=True)
#     # Merge average scores with student data
#     student_data = presentation_data[presentation_data['id_student'] == student_id]
#     comparison_data = pd.merge(student_data, avg_scores, on='id_assessment')
#     return comparison_data[['id_assessment', 'score', 'avg_score']]

