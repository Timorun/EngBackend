from flask import Blueprint, request, jsonify
import pandas as pd
from flask import current_app


student = Blueprint('student', __name__, url_prefix='/api')


@student.route('/studentids')
def get_student_ids():
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


@student.route('/studentassessment')
# This function will track an individual student's assessment scores over time within a specific course.
def student_performance_trend():
    print(request.args.values())
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
        "message": "Student IDs found",
        "student_assessments": performance_data
    })

# # This function analyzes a student’s interaction with VLE materials over time within a specific module-presentation.
# def student_engagement_trend(student_id, code_module, code_presentation, studentVle):
#     # Filter for the specific student and module-presentation
#     student_data = studentVle[(studentVle['id_student'] == student_id) &
#                               (studentVle['code_module'] == code_module) &
#                               (studentVle['code_presentation'] == code_presentation)]
#     # Group by date and sum the interactions
#     engagement_data = student_data.groupby('date')['sum_click'].sum().reset_index()
#     return engagement_data
#
#
# # This function checks if a student tends to submit assessments early, on time, or late within a specific module-presentation.
# def assessment_submission_timeliness(student_id, code_module, code_presentation, assessments, studentassessment):
#     # Merge the dataframes
#     merged_data = pd.merge(studentassessment, assessments, on='id_assessment')
#     # Filter for the specific student and module-presentation
#     student_data = merged_data[(merged_data['id_student'] == student_id) &
#                                (merged_data['code_module'] == code_module) &
#                                (merged_data['code_presentation'] == code_presentation)]
#     # Calculate submission timeliness
#     student_data['submission_timeliness'] = student_data['date_submitted'] - student_data['date']
#     return student_data[['id_assessment', 'date_submitted', 'date', 'submission_timeliness']]
#
#
#
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
#
#
#
#
#
#
# if __name__ == '__main__':
#     data = loaddata()
#
#     # performance_data = student_performance_trend(1398489, 'FFF', '2014B', data['assessments'], data['student_assessment'])
#     # print(performance_data)
#
#
#     # engagement_data = student_engagement_trend(1398489,'FFF', '2014B', data['student_vle'])
#     # print(engagement_data)
#
#
#     submission_timeliness = assessment_submission_timeliness(1398489,'FFF', '2014B', data['assessments'], data['student_assessment'])
#     print(submission_timeliness)
#
#
#     comparison = comparison_with_peers(1398489, 'FFF', '2014B', data['assessments'], data['student_assessment'])
#     print(comparison)