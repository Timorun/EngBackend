import os
import joblib
import pandas as pd
from lib_ml.data_utils import oulad_config, oulad_preprocessing
from definitions import RESOURCES_DIR, OULAD_DATA_DIR
from lib_ml.ml_utils import lightgbm_trainer


def main():
    final_df = pd.read_csv(os.path.join(RESOURCES_DIR, 'data/oulad/final_df.csv'))

    # Filter to keep rows with code_presentation as '2014J' from the final dataframe, so we only keep last semester data
    final_df = final_df[final_df['code_presentation'] == '2014J']
    print("structured")

    # Define target variable: at-risk students (e.g., based on final_result)
    final_df['at_risk'] = final_df['final_result'].apply(lambda x: 1 if x in ['Fail', 'Withdrawn'] else 0)

    # Get OULAD config and scenarios
    config = oulad_config.get_oulad_config()
    scenarios = oulad_config.get_oulad_features_by_scenario(final_df, target_col='at_risk')
    scenario_details = scenarios['engagement_only']
    # scenario_details = scenarios['total_engagement_only']
    print("scenario")

    # Load the label encoder
    label_encoders = joblib.load(os.path.join(RESOURCES_DIR, 'models/LGBMRISK/engagement_only_date100/label_encoders.joblib'))
    # label_encoders = joblib.load(os.path.join(RESOURCES_DIR, 'models/LGBMRISK/total_engagement_only_date100/label_encoders.joblib'))

    # Preprocess data for the current scenario and date
    final_df, label_encoders = oulad_preprocessing.preprocess_data(
        final_df=final_df,
        categorical_cols=config['all']['categorical'],
        features=scenario_details['features'],
        target_col=scenario_details['target'],
        DATE=100,
        label_encoders=label_encoders
    )
    print("preproc")
    print(final_df)

    lightgbm_trainer.test_lightgbm(os.path.join(RESOURCES_DIR, 'models/LGBMRISK/engagement_only_date100/lightgbm_model.pkl'),
                                   final_df, scenario_details['target'], scenario_details['features'])

    # lightgbm_trainer.test_lightgbm(os.path.join(RESOURCES_DIR, 'models/LGBMRISK/total_engagement_only_date100/lightgbm_model.pkl'),
    #     final_df, scenario_details['target'], scenario_details['features'])


if __name__ == '__main__':
    data_folder = OULAD_DATA_DIR
    final_df = pd.read_csv(os.path.join(RESOURCES_DIR, 'data/oulad/final_df.csv'))
    randstudent = final_df[final_df['id_student'] == 35340]
    print(randstudent['date'])

    # main()

