import csv
import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from definitions import DATABASE

courseblueprint = Blueprint('courseaccess', __name__, url_prefix='/api')


# Return a list of accessible courses for that user
@courseblueprint.route('/courses')
@jwt_required()
def get_courses():
    print("Courselist fetch attempt")
    current_user = get_jwt_identity()
    print(current_user)

    accessible_courses = []

    try:
        with open(os.path.join(DATABASE, 'courseaccess.csv'), 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['user_id'] == current_user:
                    course_info = (row['module_code'], row['presentation_code'])
                    if course_info not in accessible_courses:
                        accessible_courses.append(course_info)

    except IOError:
        return jsonify({"error": "Failed to read course data"}), 500

    return jsonify({
        "message": "Accessible Courses for User",
        "user_id": current_user,
        "accessible_courses": accessible_courses
    })


# Returns true if access is authorized to course
@courseblueprint.route('/courseaccess')
@jwt_required()
def checkcourseaccess():
    current_user = get_jwt_identity()

    module_code = request.args.get('module_code')
    presentation_code = request.args.get('presentation_code')

    if not module_code or not presentation_code:
        return jsonify({"error": "Module code and presentation code are required"}), 400

    courses = []

    try:
        with open(os.path.join(DATABASE, 'courseaccess.csv'), 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if (row['user_id'] == current_user and
                        row['module_code'] == module_code and
                        row['presentation_code'] == presentation_code):
                    # Append a tuple of (module_code, presentation_code) to the courses list
                    return jsonify({
                        "message": "Accessing data Course: " + str(module_code) + str(presentation_code),
                        "access": True
                    })
                    courses.append((module_code, presentation_code))

    except IOError:
        return jsonify({"error": "Failed to read course data"}), 500
