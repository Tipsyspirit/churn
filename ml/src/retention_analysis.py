import os
import joblib
import pandas as pd

from retention_strategy import recommend_retention_action

DATA_FILE = "data/E Commerce Dataset.xlsx"
MODEL_FILE = "model/customer_churn_model.joblib"
OUTPUT_FILE = "predictions/customer_retention_recommendations.csv"

def run_retention_analysis():
    # Load dataset and trained model
    df = pd.read_excel(DATA_FILE, sheet_name="E Comm")
    saved_data = joblib.load(MODEL_FILE)
    model = saved_data["model"]

    print(f"Loaded {len(df)} customer records.")
    print("Generating predictions in batch...")

    # Use the exact features expected by the trained model
    feature_columns = (
    saved_data["numerical_features"]
    + saved_data["categorical_features"]
    )
    X = df[feature_columns]

    # Predict all customers together
    probabilities = model.predict_proba(X)[:, 1]
    predictions = model.predict(X)

    results = []

    for i, (_, customer) in enumerate(df.iterrows()):
        churn_probability = float(probabilities[i])
        predicted_churn = int(predictions[i])

        if churn_probability >= 0.7:
            risk_category = "High"
        elif churn_probability >= 0.4:
            risk_category = "Medium"
        else:
            risk_category = "Low"

        customer_details = customer.to_dict()

        recommendation = recommend_retention_action(
            customer_details, risk_category
        )

        results.append({
            "CustomerID": customer.get("CustomerID"),
            "ChurnProbability": round(churn_probability, 4),
            "PredictedChurn": predicted_churn,
            "RiskCategory": recommendation["risk_category"],
            "RetentionPriority": recommendation["priority"],
            "RecommendedActions": " | ".join(
                recommendation["recommended_actions"]
            )
        })

    output = pd.DataFrame(results)

    os.makedirs("predictions", exist_ok=True)
    output.to_csv(OUTPUT_FILE, index=False)

    print("\nRetention Analysis Completed Successfully!")
    print(f"Customers analysed: {len(output)}")
    print(f"Output saved to: {OUTPUT_FILE}")

    print("\nRisk category distribution:")
    print(output["RiskCategory"].value_counts())

    print("\nSample recommendations:")
    print(output.head(5).to_string(index=False))


if __name__ == "__main__":
    run_retention_analysis()