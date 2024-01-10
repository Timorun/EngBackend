def get_oulad_config():
    # Define the configuration for categorical and numerical columns
    config = {
        'courses': {
            'categorical': ['code_module', 'code_presentation'],
            'numerical': ['module_presentation_length']
        },
        'assessments': {
            'categorical': ['code_module', 'code_presentation', 'assessment_type'],
            'numerical': ['id_assessment', 'date', 'weight']
        },
        'vle': {
            'categorical': ['id_site', 'code_module', 'code_presentation', 'activity_type'],
            'numerical': ['week_from', 'week_to']
        },
        'student_info': {
            'categorical': ['code_module', 'code_presentation', 'gender', 'region', 'highest_education', 'imd_band',
                            'age_band', 'disability', 'final_result'],
            'numerical': ['id_student', 'num_of_prev_attempts', 'studied_credits']
        },
        'student_registration': {
            'categorical': ['code_module', 'code_presentation'],
            'numerical': ['id_student', 'date_registration', 'date_unregistration']
        },
        'student_assessment': {
            'categorical': ['id_assessment', 'is_banked'],
            'numerical': ['id_student', 'date_submitted', 'score']
        },
        'student_vle': {
            'categorical': ['code_module', 'code_presentation', 'id_student', 'id_site'],
            'numerical': ['date', 'sum_click']
        }
    }

    config['all'] = {
        'categorical': list(
            set([item for sublist in [config[key]['categorical'] for key in config.keys()] for item in sublist])),
        'numerical': list(
            set([item for sublist in [config[key]['numerical'] for key in config.keys()] for item in sublist]))
    }

    return config


def get_oulad_features_by_scenario(final_df, target_col='final_result'):
    """
    Determine the feature columns to use from the OULAD dataset based on different scenarios.

    Parameters:
    final_df (DataFrame): The final merged dataframe from previous steps.
    target_col (str): The name of the target column.

    Returns:
    dict: Dictionary with scenarios as keys and dict of 'features' list and 'target' string as values.
    """

    # Initialize the dictionary to hold different scenarios
    scenarios = {}

    # Scenario 1: interactions per activity type
    engagement_features = [col for col in final_df.columns if "cumulative_clicks_" in col]
    scenarios['engagement_only'] = {'features': engagement_features, 'target': target_col}

    # Scenario 2: Total interactions Only
    total_engagement_features = ['total_cumulative_clicks']
    scenarios['total_engagement_only'] = {'features': total_engagement_features, 'target': target_col}

    # Scenario 3: All Columns Except Target(final_result)
    all_features = list(final_df.columns)
    if target_col in final_df.columns:
        all_features.remove(target_col)  # Exclude the target variable from features
    scenarios['all_columns'] = {'features': all_features, 'target': target_col}

    # Scenario 4: Only Columns Pertaining to Student Info
    # Assuming you have a list or pattern to identify student info related columns
    student_info_features = [col for col in final_df.columns if
                             "cumulative_clicks_" not in col]
    scenarios['student_info_only'] = {'features': student_info_features, 'target': target_col}

    return scenarios
