# Data processing in attempt to build LGBM with simpler features
import numpy as np
import seaborn as sns
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from definitions import OULAD_DATA_DIR
from lib_ml.data_utils.oulad_preprocessing import load_data


# Restructure and preprocess the data to have a dataframe at certain days, with total clicks, std clicks and avg per day
# If student list provided then filter to those ids
def preprocess_oulad(days, studentlist):
    datasets = load_data(data_folder=OULAD_DATA_DIR)

    # Filter out data after set date
    student_vle = datasets['student_vle']
    student_vle = student_vle[student_vle['date'] < days]

    # if not training model
    if studentlist is not None:
        # filter to studentlist, and sort to studentlist order
        student_vle = student_vle[student_vle['id_student'].isin(studentlist)]
        # Sort the DataFrame according to the order in studentlist
        # Convert 'id_student' to a categorical variable with specified order
        student_vle['id_student'] = pd.Categorical(student_vle['id_student'], categories=studentlist, ordered=True)
        student_vle = student_vle.sort_values('id_student')


    # Aggregating the data at a student-module-presentation level with features total clicks, avgclicks p day, days interacted and std clicks per day
    agg_features = student_vle.groupby(['id_student', 'code_module', 'code_presentation'], observed=False).agg(
        total_clicks=pd.NamedAgg(column='sum_click', aggfunc='sum'),
        avg_clicks_per_day=pd.NamedAgg(column='sum_click', aggfunc='mean'),
        days_interacted=pd.NamedAgg(column='date', aggfunc=lambda x: len(set(x))),
        std_clicks_per_day=pd.NamedAgg(column='sum_click', aggfunc='std')
    ).reset_index()

    # Filling NaN values in std_clicks_per_day with 0 (occurs when a student has interactions on only one day)
    agg_features['std_clicks_per_day'].fillna(0, inplace=True)

    # Display the first few rows of the aggregated features
    agg_features.head()

    # Load the studentInfo.csv file
    student_info = datasets['student_info']

    # Selecting only the necessary columns (id_student, code_module, code_presentation, final_result)
    final_result_df = student_info[['id_student', 'code_module', 'code_presentation', 'final_result']]
    # print(final_result_df)

    # Merging the final result data with the aggregated interaction data
    merged_data = pd.merge(agg_features, final_result_df, on=['id_student', 'code_module', 'code_presentation'])

    # print(merged_data)

    # Drop id_student as we do not want to predict using this
    merged_data.drop(['id_student'], axis=1, inplace=True)

    # Display the first few rows of the merged dataframe
    return merged_data


# Encode categorical labels, final result, module and presentation code, set values final res needed for LGBM: 0 to 3
def encodeandlabel(merged_data):
    # Assume merged_data is your DataFrame
    unique_code_module = merged_data['code_module'].unique()
    unique_code_presentation = merged_data['code_presentation'].unique()

    # Combine all unique values, making sure 'Withdrawn', 'Fail', 'Pass', 'Distinction' are first
    combined_classes = ['Withdrawn', 'Fail', 'Pass', 'Distinction'] + list(set(unique_code_module) | set(unique_code_presentation))

    # Create and set up the LabelEncoder with combined classes
    label_encoder = LabelEncoder()
    label_encoder.classes_ = np.array(combined_classes)

    # Encode the columns
    merged_data['final_result_encoded'] = label_encoder.transform(merged_data['final_result'])
    merged_data['code_module_encoded'] = label_encoder.transform(merged_data['code_module'])
    merged_data['code_presentation_encoded'] = label_encoder.transform(merged_data['code_presentation'])

    # Drop original categorical columns
    encoded_data = merged_data.drop(['code_module', 'code_presentation', 'final_result'], axis=1)

    # Split data into features (X) and target variable (y)
    X = encoded_data.drop('final_result_encoded', axis=1)
    y = encoded_data['final_result_encoded']

    return X, y, label_encoder
