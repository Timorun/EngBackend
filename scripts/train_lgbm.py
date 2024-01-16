# train_lgbm.py
import argparse
import os

import joblib
import pandas as pd

from lib_ml.ml_utils import lightgbm_trainer
from lib_ml.data_utils import oulad_config, oulad_preprocessing
from definitions import OULAD_DATA_DIR, MODEL_DIR, RESOURCES_DIR


def main(scenario_name, date):
    # Load restructured data
    final_df = pd.read_csv(os.path.join(RESOURCES_DIR, 'data/oulad/final_df.csv'))

    # Define target variable: at-risk students (e.g., based on final_result)
    final_df['at_risk'] = final_df['final_result'].apply(lambda x: 1 if x in ['Fail', 'Withdrawn'] else 0)

    # Get OULAD config and scenarios
    config = oulad_config.get_oulad_config()
    scenarios = oulad_config.get_oulad_features_by_scenario(final_df, target_col='at_risk')

    # Check if scenario exists
    if scenario_name not in scenarios:
        raise ValueError(f"Scenario {scenario_name} not found in available scenarios.")

    scenario_details = scenarios[scenario_name]

    # Define the folder to save models and results
    scenario_folder = os.path.join(MODEL_DIR, 'LGBMRISK', f'{scenario_name}_date{date}')
    os.makedirs(scenario_folder, exist_ok=True)

    print(final_df.shape)
    print(final_df.head())

    # Filter out rows code_presentation '2014J', we don't train with last semester data on which we will test the model
    final_df = final_df[final_df['code_presentation'] != '2014J']

    # Preprocess data for the current scenario and date
    final_df, label_encoders = oulad_preprocessing.preprocess_data(
        final_df=final_df,
        categorical_cols=config['all']['categorical'],
        features=scenario_details['features'],
        target_col=scenario_details['target'],
        DATE=date
    )

    print(final_df.shape)
    print(final_df.head())

    print("Size of final_df:", final_df.shape)

    # Save label encoders, eg to test in training and use model later
    joblib.dump(label_encoders, os.path.join(scenario_folder, 'label_encoders.joblib'))


    # Train the model and save results
    # Here we should remove last semester from final_df, data is training+validation, as we later apply on last semester
    trained_model = lightgbm_trainer.train_lightgbm(
        data=final_df,
        target=scenario_details['target'],
        features=scenario_details['features'],
        folder=scenario_folder
    )

    print(f"Model trained for {scenario_name} on date {date} and saved in {scenario_folder}")


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description="Train a LightGBM model on OULAD dataset for various scenarios.")
    # parser.add_argument("scenario", help="Scenario name to train")
    # parser.add_argument("date", type=int, help="Date to filter data for training")
    # args = parser.parse_args()

    # python -m scripts.train_lgbm engagement_only 100
    # python -m scripts.train_lgbm total_engagement_only 100

    # Restructure and saved the dataframe
    data_folder = OULAD_DATA_DIR
    datasets = oulad_preprocessing.load_data(data_folder)
    dataframe = oulad_preprocessing.restructure_data(datasets)
    output_file_path = os.path.join(OULAD_DATA_DIR, 'final_df.csv')
    dataframe.to_csv(output_file_path, index=False)

    # main(args.scenario, args.date)


