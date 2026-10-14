import os
import joblib
import pandas as pd


MODEL_FILE = "model/customer_churn_model.joblib"

ID_COLUMN = "CustomerID"
TARGET = "Churn"


def load_churn_model(model_path=MODEL_FILE):
    """
    Load the trained customer churn model.
    """

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found: {model_path}\n"
            "Run src/train.py first."
        )

    return joblib.load(model_path)


def get_risk_category(probability):
    """
    Convert churn probability into a risk category.
    """

    if probability < 0.40:
        return "Low"

    elif probability < 0.70:
        return "Medium"

    else:
        return "High"


def predict_churn(customer_data, model_path=MODEL_FILE):
    """
    Predict churn probability and risk for a customer.

    Parameters
    ----------
    customer_data : pandas.DataFrame
        One customer record.

    Returns
    -------
    dict
        Churn probability, predicted churn,
        risk category, and threshold.
    """

    if not isinstance(customer_data, pd.DataFrame):
        raise TypeError(
            "customer_data must be a pandas DataFrame."
        )

    if len(customer_data) != 1:
        raise ValueError(
            "customer_data must contain exactly one customer."
        )

    artifact = load_churn_model(model_path)

    model = artifact["model"]
    threshold = artifact["threshold"]

    data = customer_data.copy()

    # CustomerID must not be used as a model feature.
    if ID_COLUMN in data.columns:
        data = data.drop(columns=[ID_COLUMN])

    # Churn is the target and must not be supplied during prediction.
    if TARGET in data.columns:
        data = data.drop(columns=[TARGET])

    probability = float(
        model.predict_proba(data)[0, 1]
    )

    predicted_churn = int(
        probability >= threshold
    )

    risk = get_risk_category(
        probability
    )

    return {
        "churn_probability": probability,
        "predicted_churn": predicted_churn,
        "risk_category": risk,
        "threshold": threshold,
    }


if __name__ == "__main__":

    print(
        "Prediction module loaded successfully."
    )

    print(
        "Use predict_churn(customer_data) "
        "from your Streamlit application."
    )
