import json
import os
from io import StringIO

import joblib
import optuna
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import lightgbm as lgb
from sklearn.model_selection import train_test_split

from definitions import LGBMCLASS
from lib_ml.data_utils.oulad_lgbm import preprocess_oulad, encodeandlabel
from lib_ml.ml_utils.featureimportance import showfeatureimportance


# Simple lgbm training
def trainlgbm(X_train, y_train):
    # Training the LightGBM model
    lgbm_classifier = LGBMClassifier(random_state=42)
    lgbm_classifier.fit(X_train, y_train)
    return lgbm_classifier


# Function to use lgbm to predict and evaluate prediction
def testlgbm(folder, X_test, y_test):
    # Load the classifier
    lgbm_classifier = joblib.load(os.path.join(folder, 'lgbmclassifier.pkl'))
    # Load the saved LabelEncoder
    labelencoder = joblib.load(os.path.join(folder, 'label_encoder.pkl'))

    # change labels to encoded
    X_test['code_module_encoded'] = labelencoder.transform(X_test['code_module'])
    X_test['code_presentation_encoded'] = labelencoder.transform(X_test['code_presentation'])

    # Drop categorical columns
    X_test = X_test.drop(['code_module', 'code_presentation'], axis=1)

    y_test = labelencoder.transform(y_test)

    # Predicting on the test set
    y_pred = lgbm_classifier.predict(X_test)
    print(y_pred)
    y_pred = y_pred.argmax(axis=1)
    print(y_pred)

    print(evaluate(y_test, y_pred, labelencoder))
    return y_pred


# # Global variables to evaluate model after finding the best params
# global ytest, ypred
# best_accuracy = 0


# Objective function for hyperparameter tuning using Optuna for LightGBM.
def objective(trial, X, y):
    param_grid = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 10000),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
        "num_leaves": trial.suggest_int("num_leaves", 20, 1000, step=20),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "min_data_in_leaf": trial.suggest_int("min_data_in_leaf", 200, 5000, step=100),
        "max_bin": trial.suggest_int("max_bin", 200, 255),
        "lambda_l1": trial.suggest_float("lambda_l1", 0, 10, step=1),
        "lambda_l2": trial.suggest_float("lambda_l2", 0, 10, step=1),
        "min_gain_to_split": trial.suggest_float("min_gain_to_split", 0, 15),
        "bagging_fraction": trial.suggest_float("bagging_fraction", 0.4, 0.9, step=0.1),
        "bagging_freq": trial.suggest_int("bagging_freq", 1, 7),
        "feature_fraction": trial.suggest_float("feature_fraction", 0.4, 0.9, step=0.1),
        "objective": "multiclass",
        "num_class": 4,
        "verbosity": -1,
        "metric": "multi_logloss"
    }

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    gbm = lgb.train(
        param_grid,
        lgb.Dataset(X_train, label=y_train),
        valid_sets=[lgb.Dataset(X_test, label=y_test)]
    )
    preds = gbm.predict(X_test)
    print(preds)
    pred_labels = preds.argmax(axis=1)
    print(pred_labels)
    accuracy = accuracy_score(y_test, pred_labels)

    return accuracy


# Train a LightGBM model with hyperparameter tuning and save the model, best parameters, and accuracy.
def adv_trainlightgbm(X, y, folder, labelencoder, n_trials=100):
    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: objective(trial, X, y), n_trials=n_trials)

    bestaccuracy = study.best_value
    best_params = study.best_params
    best_params['objective'] = 'multiclass'
    best_params['num_class'] = 4
    best_params['metric'] = 'multi_logloss'
    final_model = lgb.train(best_params, lgb.Dataset(X, label=y))

    # Evaluate the model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    predictions = final_model.predict(X_test).argmax(axis=1)
    evaluation = evaluate(y_test, predictions, labelencoder)
    showfeatureimportance(final_model, X_train)

    os.makedirs(folder, exist_ok=True)

    # Save the model
    joblib.dump(final_model, os.path.join(folder, 'lgbmclassifier.pkl'))

    # Save the best parameters
    with open(os.path.join(folder, 'lightgbm_best_params.json'), 'w') as f:
        json.dump(best_params, f)

    # Save the evaluation result
    with open(os.path.join(folder, 'evaluation_result.txt'), 'w') as f:
        f.write(evaluation)

    # Save the best accuracy
    with open(os.path.join(folder, 'lightgbm_best_accuracy.txt'), 'w') as f:
        f.write(f"Best Accuracy: {bestaccuracy}")

    # global best_accuracy
    # best_accuracy = 0

    return final_model


# Evaluating the model's performance from actual final result and predictions
def evaluate(y_test, y_pred, labelencoder):
    y_test = labelencoder.inverse_transform(y_test)
    y_pred = labelencoder.inverse_transform(y_pred)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    classification_rep = classification_report(y_test, y_pred)

    result = (
        f"Accuracy: {accuracy}\n"
        f"Precision: {precision}\n"
        f"Recall: {recall}\n"
        f"F1 Score: {f1}\n"
        f"Classification Report:\n{classification_rep}"
    )

    return result


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

    folder = os.path.join(LGBMCLASS, f'finalclassifierdate{days}')
    # folder = os.path.join(LGBMCLASS, f'400trialsclassifierdate{days}')
    os.makedirs(folder, exist_ok=True)
    if days == "total":
        days = 300
    # set to 300 as all courses have less than that

    # Preprocess the data
    merged_data = preprocess_oulad(days, None)

    X, y, labelencoder = encodeandlabel(merged_data)
    # Store labelencoder
    joblib.dump(labelencoder, os.path.join(folder, 'label_encoder.pkl'))

    # # Train and store classifier (SIMPLE Model fitting)
    # # split into training and testing sets
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    # lgbmclassifier = trainlgbm(X_train, y_train)
    # joblib.dump(lgbmclassifier, os.path.join(folder, 'lgbmclassifier.pkl'))
    # y_pred = testlgbm(folder, X_test, y_test)
    # Get feature importance
    # showfeatureimportance(lgbmclassifier, X_train)
    # Visualize model predictions and reality of final result
    # visualizemodel(days, y_test, y_pred)

    # More advanced LGBM training with Optuna
    lgbmclassifier = adv_trainlightgbm(X, y, folder, labelencoder, 100)


# Given a list of students and how many days into the course we are, return predictions of final result
# Requires model to be trained on specific date beforehand.
def generate_predictions(days, studentidlist):
    path = os.path.join(LGBMCLASS, f'finalclassifierdate{days}')
    if days is None:
        path = os.path.join(LGBMCLASS, f'finalclassifierdatetotal')
        days = 300
    # Load the trained classifier
    classifier = joblib.load(os.path.join(path, 'lgbmclassifier.pkl'))

    # Preprocess the new data (this function should be the same as used during training)
    # Make sure to include all necessary preprocessing steps
    preprocessed_data = preprocess_oulad(days, studentidlist)
    print(preprocessed_data)

    # Encode categorical values with label_encoder used when building the model
    labelencoder = joblib.load(os.path.join(path, 'label_encoder.pkl'))
    preprocessed_data['code_module_encoded'] = labelencoder.transform(preprocessed_data['code_module'])
    preprocessed_data['code_presentation_encoded'] = labelencoder.transform(preprocessed_data['code_presentation'])

    # Drop categorical columns
    encoded_data = preprocessed_data.drop(['code_module', 'code_presentation', 'final_result'], axis=1)

    # Generate predictions
    preds = classifier.predict(encoded_data)
    print(preds)
    predictions = preds.argmax(axis=1)
    print(predictions)

    # Convert numerical predictions back to labels
    labelencoder = joblib.load(os.path.join(path, 'label_encoder.pkl'))
    predictions = labelencoder.inverse_transform(predictions)

    return predictions


# Evaluate model by retraining it with the best params in the folder
def evaluateparamsmodel():
    folder = os.path.join(LGBMCLASS, f'advclassifierdatetotal')
    folder = os.path.join(LGBMCLASS, f'FIXadvclassifierdatetotal')
    # folder = os.path.join(LGBMCLASS, f'200trialsclassifierdatetotal')
    # folder = os.path.join(LGBMCLASS, f'archive/advclassifierdatetotal')

    # Load labelencoder
    labelencoder = joblib.load(os.path.join(folder, 'label_encoder.pkl'))

    # Preprocess the data SET DAYS
    merged_data = preprocess_oulad(300, None)
    # Encode the columns
    merged_data['final_result_encoded'] = labelencoder.transform(merged_data['final_result'])
    merged_data['code_module_encoded'] = labelencoder.transform(merged_data['code_module'])
    merged_data['code_presentation_encoded'] = labelencoder.transform(merged_data['code_presentation'])
    # Drop original categorical columns
    encoded_data = merged_data.drop(['code_module', 'code_presentation', 'final_result'], axis=1)

    X = encoded_data[
        ['code_module_encoded', 'code_presentation_encoded', 'total_clicks', 'days_interacted',
         'std_weekly_clicks']]
    y = encoded_data['final_result_encoded']

    # Load parameters from JSON file
    with open(os.path.join(folder, 'lightgbm_best_params.json'), 'r') as f:
        best_params = json.load(f)
    best_params['objective'] = 'multiclass'
    best_params['num_class'] = 4
    best_params['metric'] = 'multi_logloss'
    final_model = lgb.train(best_params, lgb.Dataset(X, label=y))
    # Make predictions
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    predictions = final_model.predict(X_test).argmax(axis=1)

    # Get feature importance
    showfeatureimportance(final_model, X_train)
    # evaluate model performance
    evaluation = evaluate(y_test, predictions, labelencoder)
    print(evaluation)


if __name__ == '__main__':
    # Set up to which date to train model or None
    days = None

    # Build a model
    # buildandstoremodel(days)
    # buildandstoremodel(132)
    # buildandstoremodel(85)
    # buildandstoremodel(56)
    # buildandstoremodel(35)

    evaluateparamsmodel()

    # Generate predictions
    # studentidlist = [141377, 102952, 75091, 62155]
    # predictions = generate_predictions(None, studentidlist)
    # print(predictions)
