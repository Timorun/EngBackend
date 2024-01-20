import os

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from definitions import LGBMCLASS


def showfeatureimportance(lgbmclassifier, X_train):
    feature_importance = lgbmclassifier.feature_importance()
    feature_names = X_train.columns

    # Create a DataFrame for visualization
    feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': feature_importance})
    print(feature_importance_df)
    # Setting 'Feature' as the index
    feature_importance_df.set_index('Feature', inplace=True)
    # Dropping rows by name
    # features_to_drop = ['id_student', 'code_module_encoded', 'code_presentation_encoded']
    # feature_importance_df = feature_importance_df.drop(features_to_drop)
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