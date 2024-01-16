import os

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from definitions import LGBMCLASS


def feature_importance(path):
    # Load the saved LabelEncoder
    lgbm_classifier = joblib.load(path)

    # Get feature importance
    feature_importance = lgbm_classifier.feature_importances_
    print(feature_importance)
    feature_names = ['total_clicks', 'avg_clicks_per_day', 'days_interacted',
                 'std_clicks_per_day', 'code_module_encoded', 'code_presentation_encoded']

    # Create a DataFrame for visualization
    feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': feature_importance})

    # Sort by importance
    feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

    # Plot
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Importance', y='Feature', data=feature_importance_df)
    plt.title('LightGBM Feature Importance')
    plt.xlabel('Importance')
    plt.ylabel('Feature')
    plt.show()


if __name__ == '__main__':
    # Path to classifier
    path = os.path.join(LGBMCLASS, f'classifierdatetotal', 'lgbmclassifier.pkl')
    feature_importance(path)