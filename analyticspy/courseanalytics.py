import pandas as pd
from lib_ml.data_utils import oulad_config, oulad_preprocessing
from definitions import OULAD_DATA_DIR, MODEL_DIR


def loaddata():
    # Load and preprocess the data
    data_folder = OULAD_DATA_DIR
    datasets = oulad_preprocessing.load_data(data_folder)

    return datasets


# Completed course analytics: #


# In progress course analytics: #

# This function calculates the average scores for each type of assessment (TMA, CMA, Exam) in a specific course.
def assessment_performance_analysis(assessments_df, student_assessment_df, code_module, code_presentation):
    # Filter for the specific course
    course_assessments = assessments_df[(assessments_df['code_module'] == code_module) &
                                        (assessments_df['code_presentation'] == code_presentation)]

    # Merge with student assessment data
    merged_df = pd.merge(course_assessments, student_assessment_df, on='id_assessment')

    # Group by assessment type and calculate average score
    performance_by_assessment = merged_df.groupby('assessment_type')['score'].mean().reset_index()

    return performance_by_assessment


# This function tracks the average weekly interaction with VLE materials for a course.
def student_engagement_vle(student_vle_df, code_module, code_presentation):
    # Filter for the specific course
    course_engagement = student_vle_df[(student_vle_df['code_module'] == code_module) &
                                       (student_vle_df['code_presentation'] == code_presentation)]

    # Group by day and calculate average clicks
    daily_engagement = course_engagement.groupby('date')['sum_click'].mean().reset_index()

    return daily_engagement


#  This function calculates the rate of unregistration for a course and shows the amount of unregistrations per day
def dropout_rates(student_registration_df, code_module, code_presentation):
    # Filter for the specific course and exclude students who unregistered before the start of the course
    course_registrations = student_registration_df[(student_registration_df['code_module'] == code_module) &
                                                   (student_registration_df['code_presentation'] == code_presentation)&
                                                   (~(student_registration_df['date_unregistration'] < 1))]

    # Total number of students
    total_students = course_registrations.shape[0]

    # Number of students who unregistered
    unregistered_students = course_registrations['date_unregistration'].notna().sum()

    # Dropout rate
    dropout_rate = (unregistered_students / total_students) * 100

    # Timing of unregistrations
    unregistration_timing = course_registrations['date_unregistration'].dropna().astype(int).value_counts().sort_index()

    return dropout_rate, unregistration_timing



if __name__ == '__main__':
    data = loaddata()

    # assessment_performance = assessment_performance_analysis(data['assessments'], data['student_assessment'], 'FFF', '2014B')
    # print(assessment_performance)

    # engagement_vle = student_engagement_vle(data['student_vle'], 'FFF', '2014B')
    # print(engagement_vle)

    # dropout_rate, unregistration_timing = dropout_rates(data['student_registration'], 'FFF', '2014B')
    # print("Dropout Rate:", dropout_rate)
    # print("Unregistration Timing:\n", unregistration_timing)

