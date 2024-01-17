import os

import joblib
import seaborn as sns
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

from definitions import LGBMCLASS, OULAD_DATA_DIR
from lib_ml.data_utils.oulad_lgbm import preprocess_oulad, labelandsplit


def trainlgbm(X_train, y_train):
    # Training the LightGBM model
    lgbm_classifier = LGBMClassifier(random_state=42)
    lgbm_classifier.fit(X_train, y_train)
    return lgbm_classifier


def testlgbm(lgbm_classifier, folder, X_test, y_test):
    # Predicting on the test set
    y_pred = lgbm_classifier.predict(X_test)

    # Load the saved LabelEncoder
    labelencoder = joblib.load(os.path.join(folder, 'label_encoder.pkl'))
    # change labels to actual final result
    y_pred = labelencoder.inverse_transform(y_pred)
    y_test = labelencoder.inverse_transform(y_test)
    # This is to have labels contains the actual representations of your predictions not encoded
    evaluate(y_test, y_pred)
    return y_pred


# Evaluating the model
def evaluate(y_test, y_pred):
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    classification_rep = classification_report(y_test, y_pred)

    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1)
    print("Classification Report:\n", classification_rep)
    return y_pred


# Print rand student results and predicted result
def visualizemodel(days, y_test, y_pred):  # For folder name
    if days is None:
        days = "total"
    folder = os.path.join(LGBMCLASS, f'classifierdate{days}')

    # Load the saved LabelEncoder
    labelencoder = joblib.load(os.path.join(folder, 'label_encoder.pkl'))
    # # change labels to actual final result
    # predicted_labels = labelencoder.inverse_transform(y_pred)
    # actual_labels = labelencoder.inverse_transform(y_test)
    # # Now labels contains the actual representations of your predictions not encoded

    # Creating a DataFrame for comparison
    comparison_df = pd.DataFrame({
        'Actual': y_test,
        # 'Actual': actual_labels,
        'Predicted': y_pred,
        # 'Predicted': predicted_labels
    })

    # Resetting index for better alignment
    comparison_df = comparison_df.reset_index(drop=True)

    # Showing a sample of the comparison DataFrame
    comparison_df_sample = comparison_df.sample(20)  # Displaying 20 random samples
    print(comparison_df_sample)


# Taking days into a course to build a model to use at that date
def buildandstoremodel(days=None):
    # For folder name
    if days is None:
        days = "total"

    folder = os.path.join(LGBMCLASS, f'classifierdate{days}')
    os.makedirs(folder, exist_ok=True)
    if days == "total":
        days = 300
    # set to 300 as all courses have less than that

    # Preprocess the data
    merged_data = preprocess_oulad(days, False, None)

    X_train, X_test, y_train, y_test, labelencoder = labelandsplit(merged_data)

    # Store labelencoder
    joblib.dump(labelencoder, os.path.join(folder, 'label_encoder.pkl'))

    # Train and store classifier
    lgbmclassifier = trainlgbm(X_train, y_train)
    joblib.dump(lgbmclassifier, os.path.join(folder, 'lgbmclassifier.pkl'))
    y_pred = testlgbm(lgbmclassifier, folder, X_test, y_test)

    # Get feature importance
    # showfeatureimportance(lgbmclassifier, X_train)

    return y_test, y_pred


def generate_predictions(days, studentidlist):
    path = os.path.join(LGBMCLASS, f'classifierdate{days}')
    # Load the trained classifier
    classifier = joblib.load(os.path.join(path, 'lgbmclassifier.pkl'))

    # Preprocess the new data (this function should be the same as used during training)
    # Make sure to include all necessary preprocessing steps
    preprocessed_data = preprocess_oulad(days, True, studentidlist)  # Replace with your actual preprocessing function

    # Encode categorical values with label_encoder used when building the model
    labelencoder = joblib.load(os.path.join(path, 'label_encoder.pkl'))
    preprocessed_data['code_module_encoded'] = labelencoder.transform(preprocessed_data['code_module'])
    preprocessed_data['code_presentation_encoded'] = labelencoder.transform(preprocessed_data['code_presentation'])

    # Drop categorical columns
    encoded_data = preprocessed_data.drop(['code_module', 'code_presentation', 'final_result'], axis=1)

    # Generate predictions
    predictions = classifier.predict(encoded_data)

    # Convert numerical predictions back to labels
    labelencoder = joblib.load(os.path.join(path, 'label_encoder.pkl'))
    predictions = labelencoder.inverse_transform(predictions)

    # Evaluating the model
    # y_test = preprocessed_data['final_result']
    # y_pred = predictions
    # evaluate(y_test, y_pred)

    return predictions


if __name__ == '__main__':
    # Set up to which date to train model or None
    days = None

    # Build a model
    y_test, y_pred = buildandstoremodel(days)
    visualizemodel(days, y_test, y_pred)

    # Generate predictions
    # studentidlist = [141377, 102952, 75091, 62155]
    # predictions = generate_predictions(days, studentidlist)
    # print(predictions)
