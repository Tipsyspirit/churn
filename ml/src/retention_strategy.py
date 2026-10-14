def recommend_retention_action(customer, risk_category):
    """
    Recommend a retention action based on customer risk
    and customer behaviour.
    """

    actions = []

    # Complaint-related action
    if customer.get("Complain", 0) == 1:
        actions.append(
            "Prioritize complaint resolution and customer support."
        )

    # Satisfaction-related action
    satisfaction = customer.get("SatisfactionScore")

    if satisfaction is not None and satisfaction <= 2:
        actions.append(
            "Contact the customer to understand dissatisfaction."
        )

    # Tenure-related action
    tenure = customer.get("Tenure")

    if tenure is not None and tenure <= 5:
        actions.append(
            "Provide onboarding assistance and a first-stage loyalty offer."
        )

    # Engagement-related action
    days_since_order = customer.get("DaySinceLastOrder")

    if days_since_order is not None and days_since_order >= 7:
        actions.append(
            "Send a personalized re-engagement offer."
        )

    # Risk-based fallback and prioritization
    if risk_category == "High":
        priority = "Urgent"
        if not actions:
            actions.append(
                "Contact the customer with a personalized retention offer."
            )

    elif risk_category == "Medium":
        priority = "Moderate"
        if not actions:
            actions.append(
                "Encourage repeat purchases through relevant offers."
            )

    else:
        priority = "Low"
        if not actions:
            actions.append(
                "Maintain engagement through loyalty benefits and updates."
            )

    return {
        "risk_category": risk_category,
        "priority": priority,
        "recommended_actions": actions
    }


if __name__ == "__main__":
    sample_customer = {
        "Complain": 1,
        "SatisfactionScore": 2,
        "Tenure": 3,
        "DaySinceLastOrder": 10
    }

    result = recommend_retention_action(
        sample_customer,
        "High"
    )

    print("Customer Retention Analysis")
    print("---------------------------")
    print("Risk Category:", result["risk_category"])
    print("Priority:", result["priority"])
    print("Recommended Actions:")

    for action in result["recommended_actions"]:
        print("-", action)
