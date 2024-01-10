# lightgbm_trainer.py
import lightgbm as lgb
import numpy as np
import optuna
import joblib
import os
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def objective(trial, X, y):
    """
    Objective function for hyperparameter tuning using Optuna for LightGBM.
    """
    param_grid = {
        "n_estimators": trial.suggest_categorical("n_estimators", [10000]),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
        "num_leaves": trial.suggest_int("num_leaves", 20, 3000, step=20),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "min_data_in_leaf": trial.suggest_int("min_data_in_leaf", 200, 10000, step=100),
        "max_bin": trial.suggest_int("max_bin", 200, 300),
        "lambda_l1": trial.suggest_float("lambda_l1", 0, 100, step=5),
        "lambda_l2": trial.suggest_float("lambda_l2", 0, 100, step=5),
        "min_gain_to_split": trial.suggest_float("min_gain_to_split", 0, 15),
        "bagging_fraction": trial.suggest_float("bagging_fraction", 0.2, 0.95, step=0.1),
        "bagging_freq": trial.suggest_categorical("bagging_freq", [1]),
        "feature_fraction": trial.suggest_float("feature_fraction", 0.2, 0.95, step=0.1),
        "objective": "multiclass",
        "num_class": 4,
        "verbosity": -1,
        "metric": "multi_logloss"
    }

    train_x, valid_x, train_y, valid_y = train_test_split(X, y, test_size=0.2)
    gbm = lgb.train(
        param_grid,
        lgb.Dataset(train_x, label=train_y),
        valid_sets=[lgb.Dataset(valid_x, label=valid_y)]
    )
    preds = gbm.predict(valid_x)
    print("PREDICTIONS ARRAY 2D or not ?:")
    print(preds)
    pred_labels = preds.argmax(axis=1)
    accuracy = accuracy_score(valid_y, pred_labels)
    return accuracy


def train_lightgbm(data, target, features, n_trials=100, folder="model_files"):
    """
    Train a LightGBM model with hyperparameter tuning and save the model, best parameters, and accuracy.
    """
    X = data[features]
    y = data[target]

    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: objective(trial, X, y), n_trials=n_trials)

    best_params = study.best_params
    best_accuracy = study.best_value
    final_model = lgb.train(best_params, lgb.Dataset(X, label=y))

    os.makedirs(folder, exist_ok=True)

    # Save the model
    joblib.dump(final_model, os.path.join(folder, 'lightgbm_model.pkl'))

    # Save the best parameters
    with open(os.path.join(folder, 'lightgbm_best_params.json'), 'w') as f:
        json.dump(best_params, f)

    # Save the best accuracy
    with open(os.path.join(folder, 'lightgbm_best_accuracy.txt'), 'w') as f:
        f.write(f"Best Accuracy: {best_accuracy}")

    return final_model


# Func to test model on any data
def test_lightgbm(model_path, data, target, features):
    """
    Import a trained LightGBM model and test it on another dataframe, returning accuracy.
    """
    model = joblib.load(model_path)
    X_test = data[features]
    y_test = data[target]

    preds = model.predict_proba(X_test)
    print(preds)
    pred_labels = preds.argmax(axis=1)
    print(pred_labels)
    accuracy = accuracy_score(y_test, pred_labels)

    return accuracy