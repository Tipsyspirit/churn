import os
import warnings
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
    precision_recall_curve,
)

from preprocessing import get_feature_columns, build_preprocessor

warnings.filterwarnings("ignore")


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = "data/E Commerce Dataset.xlsx"
SHEET_NAME = "E Comm"

TARGET = "Churn"
ID_COLUMN = "CustomerID"

MODEL_FILE = "model/customer_churn_model.joblib"
PREDICTION_FILE = "predictions/customer_churn_predictions.csv"

RANDOM_STATE = 42


# ============================================================
# CREATE OUTPUT DIRECTORIES
# ============================================================

os.makedirs("model", exist_ok=True)
os.makedirs("predictions", exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}\n"
        "Place the real E Commerce Dataset.xlsx file inside the data folder."
    )

df = pd.read_excel(
    DATA_FILE,
    sheet_name=SHEET_NAME
)

print("=" * 70)
print("DATASET")
print("=" * 70)

print("Shape:", df.shape)
print("Columns:", df.columns.tolist())


# ============================================================
# DATA QUALITY CHECK
# ============================================================

print("\n" + "=" * 70)
print("DATA QUALITY")
print("=" * 70)

print("\nMissing values:")
print(df.isnull().sum()[df.isnull().sum() > 0])

print("\nDuplicate rows:", df.duplicated().sum())

print("\nTarget distribution:")
print(df[TARGET].value_counts())

print("\nTarget percentage:")
print(
    (df[TARGET].value_counts(normalize=True) * 100).round(2)
)

if ID_COLUMN in df.columns:
    print(
        "\nDuplicate CustomerIDs:",
        df[ID_COLUMN].duplicated().sum()
    )


# Remove exact duplicate rows
df = df.drop_duplicates().reset_index(drop=True)

# Remove rows where target is missing
df = df.dropna(subset=[TARGET]).reset_index(drop=True)


# ============================================================
# FEATURES AND TARGET
# ============================================================

drop_columns = [TARGET]

if ID_COLUMN in df.columns:
    drop_columns.append(ID_COLUMN)

X = df.drop(columns=drop_columns)
y = df[TARGET].astype(int)

numerical_features, categorical_features = get_feature_columns(X)

print("\n" + "=" * 70)
print("FEATURES")
print("=" * 70)

print("\nNumerical features:")
print(numerical_features)

print("\nCategorical features:")
print(categorical_features)

print("\nTotal features:", X.shape[1])


# ============================================================
# TRAIN / VALIDATION / TEST SPLIT
# ============================================================

X_temp, X_test, y_temp, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=RANDOM_STATE,
)

X_train, X_valid, y_train, y_valid = train_test_split(
    X_temp,
    y_temp,
    test_size=0.25,
    stratify=y_temp,
    random_state=RANDOM_STATE,
)

print("\n" + "=" * 70)
print("DATA SPLIT")
print("=" * 70)

print("Training:", X_train.shape)
print("Validation:", X_valid.shape)
print("Testing:", X_test.shape)


# ============================================================
# PREPROCESSOR
# ============================================================

preprocessor = build_preprocessor(
    numerical_features,
    categorical_features
)


# ============================================================
# BASELINE EXTRA TREES
# ============================================================

baseline_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            ExtraTreesClassifier(
                n_estimators=300,
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
        ),
    ]
)

baseline_model.fit(X_train, y_train)

baseline_probability = baseline_model.predict_proba(
    X_valid
)[:, 1]

baseline_prediction = (
    baseline_probability >= 0.50
).astype(int)

baseline_pr_auc = average_precision_score(
    y_valid,
    baseline_probability
)

baseline_roc_auc = roc_auc_score(
    y_valid,
    baseline_probability
)

print("\n" + "=" * 70)
print("BASELINE EXTRA TREES")
print("=" * 70)

print("ROC-AUC:", round(baseline_roc_auc, 4))
print("PR-AUC :", round(baseline_pr_auc, 4))


# ============================================================
# HYPERPARAMETER TUNING
# ============================================================

tuning_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            ExtraTreesClassifier(
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
        ),
    ]
)

param_distributions = {
    "classifier__n_estimators": [200, 300, 500],
    "classifier__max_depth": [None, 10, 20, 30],
    "classifier__min_samples_split": [2, 5, 10],
    "classifier__min_samples_leaf": [1, 2, 4],
    "classifier__max_features": ["sqrt", "log2", None],
}

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=RANDOM_STATE,
)

search = RandomizedSearchCV(
    estimator=tuning_pipeline,
    param_distributions=param_distributions,
    n_iter=15,
    scoring="average_precision",
    cv=cv,
    random_state=RANDOM_STATE,
    n_jobs=-1,
    verbose=1,
)

search.fit(X_train, y_train)

best_pipeline = search.best_estimator_

print("\n" + "=" * 70)
print("TUNING RESULT")
print("=" * 70)

print("Best parameters:")
print(search.best_params_)

print(
    "\nBest cross-validation PR-AUC:",
    round(search.best_score_, 4)
)


# ============================================================
# VALIDATION PROBABILITIES
# ============================================================

validation_probability = best_pipeline.predict_proba(
    X_valid
)[:, 1]

validation_roc_auc = roc_auc_score(
    y_valid,
    validation_probability
)

validation_pr_auc = average_precision_score(
    y_valid,
    validation_probability
)

print("\n" + "=" * 70)
print("VALIDATION PERFORMANCE")
print("=" * 70)

print("ROC-AUC:", round(validation_roc_auc, 4))
print("PR-AUC :", round(validation_pr_auc, 4))


# ============================================================
# THRESHOLD OPTIMIZATION
# ============================================================

precision, recall, thresholds = precision_recall_curve(
    y_valid,
    validation_probability
)

f1_scores = (
    2 * precision[:-1] * recall[:-1]
    / (
        precision[:-1]
        + recall[:-1]
        + 1e-12
    )
)

best_index = np.argmax(f1_scores)

best_threshold = float(
    thresholds[best_index]
)

print("\n" + "=" * 70)
print("THRESHOLD OPTIMIZATION")
print("=" * 70)

print(
    "Optimized threshold:",
    round(best_threshold, 4)
)

print(
    "Validation precision:",
    round(precision[best_index], 4)
)

print(
    "Validation recall:",
    round(recall[best_index], 4)
)

print(
    "Validation F1:",
    round(f1_scores[best_index], 4)
)


# ============================================================
# FINAL TRAINING
# TRAIN + VALIDATION
# ============================================================

X_train_final = pd.concat(
    [X_train, X_valid]
)

y_train_final = pd.concat(
    [y_train, y_valid]
)

final_preprocessor = build_preprocessor(
    numerical_features,
    categorical_features
)

final_model = ExtraTreesClassifier(
    **{
        key.replace("classifier__", ""): value
        for key, value in search.best_params_.items()
    },
    class_weight="balanced",
    random_state=RANDOM_STATE,
    n_jobs=-1,
)

final_pipeline = Pipeline(
    steps=[
        ("preprocessor", final_preprocessor),
        ("classifier", final_model),
    ]
)

final_pipeline.fit(
    X_train_final,
    y_train_final
)


# ============================================================
# FINAL TEST EVALUATION
# ============================================================

test_probability = final_pipeline.predict_proba(
    X_test
)[:, 1]

test_prediction = (
    test_probability >= best_threshold
).astype(int)

accuracy = accuracy_score(
    y_test,
    test_prediction
)

precision_score_value = precision_score(
    y_test,
    test_prediction,
    zero_division=0
)

recall_score_value = recall_score(
    y_test,
    test_prediction,
    zero_division=0
)

f1 = f1_score(
    y_test,
    test_prediction,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    test_probability
)

pr_auc = average_precision_score(
    y_test,
    test_probability
)


print("\n" + "=" * 70)
print("FINAL TEST RESULTS")
print("=" * 70)

print(
    classification_report(
        y_test,
        test_prediction,
        target_names=["No Churn", "Churn"],
        zero_division=0,
    )
)

print("Confusion Matrix:")
print(confusion_matrix(y_test, test_prediction))

print("\nAccuracy :", round(accuracy, 4))
print("Precision:", round(precision_score_value, 4))
print("Recall   :", round(recall_score_value, 4))
print("F1       :", round(f1, 4))
print("ROC-AUC  :", round(roc_auc, 4))
print("PR-AUC   :", round(pr_auc, 4))


# ============================================================
# RISK CLASSIFICATION
# ============================================================

def risk_category(probability):

    if probability < 0.40:
        return "Low"

    elif probability < 0.70:
        return "Medium"

    else:
        return "High"


# ============================================================
# GENERATE TEST PREDICTIONS
# ============================================================

prediction_output = X_test.copy()

if ID_COLUMN in df.columns:

    prediction_output.insert(
        0,
        ID_COLUMN,
        df.loc[X_test.index, ID_COLUMN].values
    )

prediction_output["Actual_Churn"] = y_test.values

prediction_output["Churn_Probability"] = (
    test_probability
)

prediction_output["Predicted_Churn"] = (
    test_prediction
)

prediction_output["Risk_Category"] = (
    prediction_output["Churn_Probability"]
    .apply(risk_category)
)

prediction_output = prediction_output.sort_values(
    "Churn_Probability",
    ascending=False
)


prediction_output.to_csv(
    PREDICTION_FILE,
    index=False
)


# ============================================================
# SAVE MODEL
# ============================================================

model_artifact = {

    "model": final_pipeline,

    "threshold": best_threshold,

    "target": TARGET,

    "id_column": ID_COLUMN,

    "numerical_features": numerical_features,

    "categorical_features": categorical_features,

    "risk_rules": {
        "Low": "Probability < 0.40",
        "Medium": "0.40 <= Probability < 0.70",
        "High": "Probability >= 0.70",
    },

    "metrics": {
        "accuracy": accuracy,
        "precision": precision_score_value,
        "recall": recall_score_value,
        "f1": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
    },
}


joblib.dump(
    model_artifact,
    MODEL_FILE
)


print("\n" + "=" * 70)
print("FILES GENERATED")
print("=" * 70)

print(
    "Model:",
    MODEL_FILE
)

print(
    "Predictions:",
    PREDICTION_FILE
)

print(
    "\nOptimized threshold:",
    round(best_threshold, 4)
)

print("\nTraining completed successfully.")
