import pandas as pd
from sklearn.preprocessing import LabelEncoder


def load_data(data_folder):
    """
    Load datasets from the specified folder.

    Parameters:
    data_folder (str): The path to the folder containing the data files.

    Returns:
    dict: A dictionary of pandas dataframes.
    """
    datasets = {
        'courses': pd.read_csv(f'{data_folder}/courses.csv'),
        'assessments': pd.read_csv(f'{data_folder}/assessments.csv'),
        'vle': pd.read_csv(f'{data_folder}/vle.csv'),
        'student_info': pd.read_csv(f'{data_folder}/studentInfo.csv'),
        'student_registration': pd.read_csv(f'{data_folder}/studentRegistration.csv'),
        'student_assessment': pd.read_csv(f'{data_folder}/studentAssessment.csv'),
        'student_vle': pd.read_csv(f'{data_folder}/studentVle.csv')
    }
    return datasets


def sample_students(datasets, n=1000, random_state=1):
    """
    Sample a subset of students from the student_info dataset and filter other dataframes
    to include only students present in the sampled student_info.

    Parameters:
    datasets (dict): A dictionary of dataframes including 'student_info'.
    n (int): Number of samples to return.
    random_state (int): Seed for the random number generator for reproducibility.

    Returns:
    dict: A dictionary of dataframes with all related datasets filtered based on sampled 'student_info'.
    """
    sampled_students = datasets['student_info'].sample(n=n, random_state=random_state)
    sampled_student_ids = set(sampled_students['id_student'])

    # Update the student_info dataframe in datasets
    datasets['student_info'] = sampled_students

    # Filter all other dataframes to include only sampled students
    for key in ['student_registration', 'student_assessment', 'student_vle']:
        datasets[key] = datasets[key][datasets[key]['id_student'].isin(sampled_student_ids)]

    return datasets


def restructure_data(datasets):
    """
    Restructure data by merging, sorting, aggregating, and calculating cumulative clicks.

    Parameters:
    datasets (dict): A dictionary of dataframes including 'student_vle', 'vle', 'student_info'.

    Returns:
    DataFrame: A dataframe with cumulative clicks and other processed information.
    """

    # Assuming all the dataframes (student_vle, vle, student_info, etc.) are loaded into the environment

    # Filter the student_vle dataframe to include only students present in the sampled student_info
    student_vle_sampled = datasets["student_vle"][
        datasets["student_vle"]['id_student'].isin(datasets["student_info"]['id_student'])]

    # Merge the vle and student_vle data on code_module, code_presentation, and id_site to get activity type for each
    # student interaction
    merged_vle = pd.merge(student_vle_sampled,
                          datasets["vle"][['id_site', 'code_module', 'code_presentation', 'activity_type']],
                          on=['id_site', 'code_module', 'code_presentation'])

    print("Size of DF1", merged_vle.shape)
    # randstudent = merged_vle[merged_vle['id_student'] == 6516]
    # print("Example student: ", randstudent['date'])

    # Filter out rows where activity_type is 'repeatactivity', because barely any interactions present in dataset
    merged_vle = merged_vle[merged_vle['activity_type'] != 'repeatactivity']

    print("Size of DF2", merged_vle.shape)
    randstudent = merged_vle[merged_vle['id_student'] == 6516]
    print("Example student: ", randstudent)

    # Ensure the data is sorted by date before calculating the cumulative sum
    merged_vle = merged_vle.sort_values(by=['id_student', 'code_module', 'code_presentation', 'activity_type', 'date'])

    # Aggregate the sum_clicks for each activity type, for a student in a course, at certain date
    aggregated_clicks = \
        merged_vle.groupby(['id_student', 'code_module', 'code_presentation', 'id_site', 'activity_type', 'date'])[
            'sum_click'].sum().reset_index()

    # Create a function to generate a complete date range for each group
    def generate_date_range(group):
        min_date = group['date'].min()
        max_date = group['date'].max()
        all_dates = pd.DataFrame({'date': range(min_date, max_date + 1)})
        return group.merge(all_dates, on='date', how='right')

    # Apply the function to each group and fill NaNs with appropriate values
    complete_data = aggregated_clicks.groupby(['id_student', 'code_module', 'code_presentation']).apply(
        generate_date_range)
    complete_data['sum_click'] = complete_data['sum_click'].fillna(0)
    complete_data = complete_data.drop(columns=['id_student', 'code_module', 'code_presentation']).reset_index()

    # Now complete_data contains rows for every date, with sum_click set to 0 where there were no interactions

    print("Size of DF3", complete_data.shape)
    randstudent = complete_data[complete_data['id_student'] == 6516]
    print("Example student: ", randstudent)

    # Ensure the data is sorted by date within each group before calculating the cumulative sum
    aggregated_clicks.sort_values(by=['id_student', 'code_module', 'code_presentation', 'activity_type', 'date'],
                                  inplace=True)

    # Calculate cumulative clicks for each activity type, ensuring only previous days are summed
    cumulative_clicks = aggregated_clicks.groupby(['id_student', 'code_module', 'code_presentation', 'activity_type'])[
        'sum_click'].cumsum()
    aggregated_clicks['cumulative_clicks'] = cumulative_clicks

    print("Size of DF4", aggregated_clicks.shape)

    # Pivot the table so that each activity type's cumulative clicks are in separate columns
    pivot_vle = aggregated_clicks.pivot_table(index=['id_student', 'code_module', 'code_presentation', 'date'],
                                              columns='activity_type',
                                              values='cumulative_clicks',
                                              aggfunc='first').reset_index()

    print("Size of DF5", pivot_vle.shape)

    # Apply forward fill within each group of 'id_student', 'code_module', 'code_presentation'
    pivot_vle = pivot_vle.groupby(['id_student', 'code_module', 'code_presentation'], as_index=False).apply(
        lambda group: group.ffill())
    # pivot_vle.reset_index(inplace=True)

    # After forward fill, replace any remaining NaNs with 0 (for the first occurrence in each group)
    pivot_vle.fillna(0, inplace=True)

    print("Size of DF5", pivot_vle.shape)

    # Rename the columns to have a clear format
    pivot_vle.columns = [
        f'cumulative_clicks_{col}' if col not in ['id_student', 'code_module', 'code_presentation', 'date'] else col for
        col in pivot_vle.columns]

    # Calculate total cumulative clicks for each row
    activity_columns = [col for col in pivot_vle.columns if 'cumulative_clicks_' in col]
    pivot_vle['total_cumulative_clicks'] = pivot_vle[activity_columns].sum(axis=1)

    print("Size of DF6", pivot_vle.shape)

    # Merge student_info to bring in additional student details
    final_df = pd.merge(pivot_vle, datasets["student_info"][
        ['id_student', 'gender', 'region', 'highest_education', 'imd_band', 'age_band', 'num_of_prev_attempts',
         'studied_credits', 'disability', 'final_result']], on='id_student', how='left')

    # Fill NaN values for student_info columns with appropriate values
    # The fill values should be determined based on the nature of your data and the analysis you intend to perform
    info_columns = ['gender', 'region', 'highest_education', 'imd_band', 'age_band', 'num_of_prev_attempts',
                    'studied_credits', 'disability', 'final_result']
    for col in info_columns:
        if final_df[col].dtype == 'object':
            final_df[col] = final_df[col].fillna('Unknown')  # Or any other placeholder for categorical data
        else:
            final_df[col] = final_df[col].fillna(0)  # Or any other placeholder for numerical data

    print("Size of DF7", pivot_vle.shape)

    print("final_df", final_df.columns)

    return final_df


def preprocess_data(final_df, categorical_cols, features, target_col, DATE, label_encoders={}):
    """
    Preprocess the OULAD dataset by encoding categorical columns and filtering by date.

    Parameters:
    final_df (DataFrame): The final merged dataframe from previous steps.
    categorical_cols (list): List of names of categorical columns to encode.
    features (list): List of feature column names to include in the model.
    target_col (str): Name of the target column.
    DATE (int): Specific date to filter the dataframe.

    Returns:
    filtered_final_df (DataFrame): The processed dataframe ready for model training or testing.
    label_encoders (dict): Dictionary of label encoders for each categorical column.
    """

    # Filter to Date
    filtered_final_df = final_df[final_df['date'] == DATE]

    # Ensure only the selected features and target column are included
    filtered_final_df = filtered_final_df[features + [target_col]]

    # Encode the categorical features
    for categorical_col in categorical_cols:
        le = LabelEncoder()
        if categorical_col in label_encoders:
            le = label_encoders[categorical_col]
        if categorical_col in filtered_final_df.columns:
            filtered_final_df[categorical_col] = le.fit_transform(filtered_final_df[categorical_col])
        label_encoders[categorical_col] = le

    return filtered_final_df, label_encoders
