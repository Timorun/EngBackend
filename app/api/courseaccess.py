import base64
import csv
import os

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from definitions import DATABASE
from lib_data.database import accesscheck

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
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                encrypted_row = row[0]
                decrypted_row_str = current_app.cipher_suite.decrypt(base64.urlsafe_b64decode(encrypted_row)).decode()
                decrypted_row = decrypted_row_str.split(',')

                if decrypted_row[0] == str(current_user):
                    course_info = (decrypted_row[1], decrypted_row[2])
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

    access = accesscheck(current_app.cipher_suite, current_user, module_code, presentation_code)

    if access:
        return jsonify({
            "message": "Accessing data Course: " + str(module_code) + str(presentation_code),
            "access": True
        })
    else:
        return jsonify({"error": "Failed to read course data"}), 500
