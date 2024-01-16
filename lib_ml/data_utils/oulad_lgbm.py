# Data processing in attempt to build LGBM with simpler features
import seaborn as sns
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from definitions import OULAD_DATA_DIR
from lib_ml.data_utils.oulad_preprocessing import load_data


def preprocess_oulad(days, use, studentlist):
    datasets = load_data(data_folder=OULAD_DATA_DIR)

    # Filter out data after set date
    student_vle = datasets['student_vle']
    student_vle = student_vle[student_vle['date'] < days]

    #if not training model
    if use:
        # filter to studentlist, and sort to studentlist order
        student_vle = student_vle[student_vle['id_student'].isin(studentlist)]
        # Sort the DataFrame according to the order in studentlist
        # Convert 'id_student' to a categorical variable with specified order
        student_vle['id_student'] = pd.Categorical(student_vle['id_student'], categories=studentlist, ordered=True)
        student_vle = student_vle.sort_values('id_student')
    #     # Filter to only rows code_presentation '2014J', we don't train with last semester data on which we will test the model
    #     student_vle = student_vle[student_vle['code_presentation'] == '2014J']
    # else:
    #     student_vle = student_vle[student_vle['code_presentation'] != '2014J']

    # Aggregating the data at a student-module-presentation level with features total clicks, avgclicks p day, days interacted and std clicks per day
    agg_features = student_vle.groupby(['id_student', 'code_module', 'code_presentation']).agg(
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


def labelandsplit(merged_data):
    # Encode the 3 categorical variables in one label encoder as values are exclusive per column
    all_categories = pd.concat([merged_data['final_result'],
                                merged_data['code_module'],
                                merged_data['code_presentation']])

    label_encoder = LabelEncoder()
    label_encoder.fit(all_categories)

    merged_data['final_result_encoded'] = label_encoder.transform(merged_data['final_result'])
    merged_data['code_module_encoded'] = label_encoder.transform(merged_data['code_module'])
    merged_data['code_presentation_encoded'] = label_encoder.transform(merged_data['code_presentation'])

    # Drop original categorical columns
    encoded_data = merged_data.drop(['code_module', 'code_presentation', 'final_result'], axis=1)

    # Split data into features (X) and target variable (y)
    X = encoded_data.drop('final_result_encoded', axis=1)
    y = encoded_data['final_result_encoded']

    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    return X_train, X_test, y_train, y_test, label_encoder
