import streamlit as st
from utils import session, api, styles
from components.kpi_cards import risk_badge

st.set_page_config(page_title="Predict · ChurnSight", layout="wide")
styles.inject()
session.init()
session.require_login()

st.title("Predict one customer")

with st.form("predict_form"):
    cid = st.text_input("Customer ID (optional)", "")
    col1, col2, col3 = st.columns(3)
    with col1:
        Tenure = st.number_input("Tenure (months)", 0.0, 100.0, 12.0)
        CityTier = st.selectbox("City Tier", [1,2,3])
        WarehouseToHome = st.number_input("Warehouse to Home (km)", 0.0, 500.0, 15.0)
        PreferredLoginDevice = st.selectbox("Login Device", ["Mobile Phone","Computer","Phone"])
        PreferredPaymentMode = st.selectbox("Payment Mode", ["Debit Card","Credit Card","E Wallet","COD","UPI"])
        Gender = st.selectbox("Gender", ["Male","Female"])
    with col2:
        HourSpendOnApp = st.number_input("Hours on App", 0.0, 24.0, 3.0)
        NumberOfDeviceRegistered = st.number_input("Devices", 1, 10, 3)
        PreferedOrderCat = st.selectbox("Preferred Category", ["Laptop & Accessory","Mobile","Mobile Phone","Fashion","Grocery","Others"])
        SatisfactionScore = st.slider("Satisfaction (1-5)", 1, 5, 3)
        MaritalStatus = st.selectbox("Marital Status", ["Single","Married","Divorced"])
    with col3:
        NumberOfAddress = st.number_input("Addresses", 1, 20, 2)
        Complain = st.selectbox("Complaint filed", [0,1])
        OrderAmountHikeFromlastYear = st.number_input("Order hike %", 0.0, 100.0, 15.0)
        CouponUsed = st.number_input("Coupons used", 0.0, 50.0, 2.0)
        OrderCount = st.number_input("Order count", 0.0, 100.0, 3.0)
        DaySinceLastOrder = st.number_input("Days since last order", 0.0, 365.0, 5.0)
        CashbackAmount = st.number_input("Cashback amount", 0.0, 10000.0, 150.0)

    submitted = st.form_submit_button("Predict", type="primary")

if submitted:
    features = {
        "Tenure": Tenure, "CityTier": CityTier, "WarehouseToHome": WarehouseToHome,
        "PreferredLoginDevice": PreferredLoginDevice,
        "PreferredPaymentMode": PreferredPaymentMode, "Gender": Gender,
        "HourSpendOnApp": HourSpendOnApp,
        "NumberOfDeviceRegistered": NumberOfDeviceRegistered,
        "PreferedOrderCat": PreferedOrderCat,
        "SatisfactionScore": SatisfactionScore, "MaritalStatus": MaritalStatus,
        "NumberOfAddress": NumberOfAddress, "Complain": Complain,
        "OrderAmountHikeFromlastYear": OrderAmountHikeFromlastYear,
        "CouponUsed": CouponUsed, "OrderCount": OrderCount,
        "DaySinceLastOrder": DaySinceLastOrder, "CashbackAmount": CashbackAmount,
    }
    try:
        result = api.predict_one(cid or "manual", features)
        p = result["churn_probability"]
        st.metric("Churn probability", f"{p*100:.1f}%")
        st.markdown(f"Risk: {risk_badge(result['risk'])}", unsafe_allow_html=True)
        st.caption(f"Model threshold: {result['threshold']:.4f}")
    except Exception as e:
        st.error(str(e))