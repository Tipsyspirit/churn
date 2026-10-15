import math
import streamlit as st
from utils import session, api, styles
from components.kpi_cards import risk_badge

st.set_page_config(page_title="Predict · ChurnSight", layout="wide")
styles.inject()
session.init()
session.require_login()


# =========================================================
# Helpers — keep JSON payload compliant
# =========================================================
def safe_float(v, default=0.0) -> float:
    """Convert to a JSON-safe float. Returns default for NaN, inf, -inf, None."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return default
    if math.isnan(f) or math.isinf(f):
        return default
    return f


def safe_int(v, default=0) -> int:
    return int(safe_float(v, default))


def safe_str(v, default="Unknown") -> str:
    if v is None:
        return default
    try:
        if isinstance(v, float) and math.isnan(v):
            return default
    except Exception:
        pass
    s = str(v).strip()
    if s == "" or s.lower() in ("nan", "none", "null"):
        return default
    return s


# =========================================================
# Page header
# =========================================================
st.markdown(
    '<div class="greeting" style="font-size:32px;">Predict one customer</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="greeting-sub" style="color:#F2F2F2; margin-bottom:20px;">'
    "Enter the customer details below, or pick an existing one from the dataset."
    "</div>",
    unsafe_allow_html=True,
)


# =========================================================
# Optional: pick an existing customer
# =========================================================
prefill = st.session_state.pop("predict_prefill", {}) or {}

if st.session_state.get("predictions") is not None:
    df = st.session_state["customers"]
    top200 = df.sort_values("churn_probability", ascending=False).head(200)
    opts = ["—"] + [str(r.customer_id) for r in top200.itertuples()]
    picked = st.selectbox("Or pick an existing customer", opts, index=0)

    if picked != "—":
        row = df[df["customer_id"].astype(str) == picked]
        if not row.empty:
            prefill = row.iloc[0].to_dict()


# =========================================================
# Prediction form
# =========================================================
with st.form("predict_form"):
    cid = st.text_input(
        "Customer ID (optional)",
        value=str(prefill.get("customer_id", "")) if prefill else "",
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        Tenure = st.number_input(
            "Tenure (months)", 0.0, 100.0,
            safe_float(prefill.get("Tenure"), 12.0),
        )
        CityTier = st.selectbox(
            "City Tier", [1, 2, 3],
            index=([1, 2, 3].index(safe_int(prefill.get("CityTier"), 1))
                   if prefill and safe_int(prefill.get("CityTier"), 1) in [1, 2, 3]
                   else 0),
        )
        WarehouseToHome = st.number_input(
            "Warehouse to Home (km)", 0.0, 500.0,
            safe_float(prefill.get("WarehouseToHome"), 15.0),
        )
        PreferredLoginDevice = st.selectbox(
            "Login Device", ["Mobile Phone", "Computer", "Phone"],
            index=(["Mobile Phone", "Computer", "Phone"].index(
                safe_str(prefill.get("PreferredLoginDevice"), "Mobile Phone"))
                if prefill and safe_str(prefill.get("PreferredLoginDevice"), "Mobile Phone")
                in ["Mobile Phone", "Computer", "Phone"] else 0),
        )
        PreferredPaymentMode = st.selectbox(
            "Payment Mode",
            ["Debit Card", "Credit Card", "E Wallet", "COD", "UPI"],
        )
        Gender = st.selectbox(
            "Gender", ["Male", "Female"],
            index=(["Male", "Female"].index(
                safe_str(prefill.get("Gender"), "Male"))
                if prefill and safe_str(prefill.get("Gender"), "Male") in ["Male", "Female"]
                else 0),
        )

    with c2:
        HourSpendOnApp = st.number_input(
            "Hours on App", 0.0, 24.0,
            safe_float(prefill.get("HourSpendOnApp"), 3.0),
        )
        NumberOfDeviceRegistered = st.number_input(
            "Devices Registered", 1, 10,
            safe_int(prefill.get("NumberOfDeviceRegistered"), 3),
        )
        PreferedOrderCat = st.selectbox(
            "Preferred Category",
            ["Laptop & Accessory", "Mobile", "Mobile Phone",
             "Fashion", "Grocery", "Others"],
        )
        SatisfactionScore = st.slider(
            "Satisfaction Score (1–5)", 1, 5,
            safe_int(prefill.get("SatisfactionScore"), 3),
        )
        MaritalStatus = st.selectbox(
            "Marital Status", ["Single", "Married", "Divorced"],
        )

    with c3:
        NumberOfAddress = st.number_input(
            "Number of Addresses", 1, 20,
            safe_int(prefill.get("NumberOfAddress"), 2),
        )
        Complain = st.selectbox(
            "Complaint Filed", [0, 1],
            index=safe_int(prefill.get("Complain"), 0) if prefill else 0,
        )
        OrderAmountHikeFromlastYear = st.number_input(
            "Order Amount Hike (%)", 0.0, 100.0,
            safe_float(prefill.get("OrderAmountHikeFromlastYear"), 15.0),
        )
        CouponUsed = st.number_input(
            "Coupons Used", 0.0, 50.0,
            safe_float(prefill.get("CouponUsed"), 2.0),
        )
        OrderCount = st.number_input(
            "Order Count", 0.0, 100.0,
            safe_float(prefill.get("OrderCount"), 3.0),
        )
        DaySinceLastOrder = st.number_input(
            "Days Since Last Order", 0.0, 365.0,
            safe_float(prefill.get("DaySinceLastOrder"), 5.0),
        )
        CashbackAmount = st.number_input(
            "Cashback Amount", 0.0, 10000.0,
            safe_float(prefill.get("CashbackAmount"), 150.0),
        )

    submitted = st.form_submit_button(
        "Predict churn", type="primary", use_container_width=True,
    )


# =========================================================
# Handle submission
# =========================================================
if submitted:
    features = {
        "Tenure": safe_float(Tenure),
        "CityTier": safe_int(CityTier, 1),
        "WarehouseToHome": safe_float(WarehouseToHome),
        "PreferredLoginDevice": safe_str(PreferredLoginDevice, "Mobile Phone"),
        "PreferredPaymentMode": safe_str(PreferredPaymentMode, "Debit Card"),
        "Gender": safe_str(Gender, "Male"),
        "HourSpendOnApp": safe_float(HourSpendOnApp),
        "NumberOfDeviceRegistered": safe_int(NumberOfDeviceRegistered, 1),
        "PreferedOrderCat": safe_str(PreferedOrderCat, "Mobile"),
        "SatisfactionScore": safe_int(SatisfactionScore, 3),
        "MaritalStatus": safe_str(MaritalStatus, "Single"),
        "NumberOfAddress": safe_int(NumberOfAddress, 1),
        "Complain": safe_int(Complain, 0),
        "OrderAmountHikeFromlastYear": safe_float(OrderAmountHikeFromlastYear),
        "CouponUsed": safe_float(CouponUsed),
        "OrderCount": safe_float(OrderCount),
        "DaySinceLastOrder": safe_float(DaySinceLastOrder),
        "CashbackAmount": safe_float(CashbackAmount),
    }

    cid_final = (cid or "").strip() or "manual"

    try:
        result = api.predict_one(cid_final, features)

        p = safe_float(result.get("churn_probability"), 0.0)
        pct = round(p * 100)
        risk = result.get("risk", "low")
        likely = int(result.get("predicted_churn", 0)) == 1
        threshold = safe_float(result.get("threshold"), 0.5)
        marker_pct = max(0, min(100, pct))

        st.markdown(
            f"""
            <div class="result-panel" style="margin-top:20px;">
                <div style="font-size:11px; letter-spacing:0.09em;
                            text-transform:uppercase; color:#636363;
                            font-weight:600;">Prediction result</div>

                <div class="result-id">{cid_final}</div>

                <div class="result-top">
                    {risk_badge(risk)}
                    <span class="outcome {'bad' if likely else 'ok'}">
                        {'Likely to churn' if likely else 'Likely to stay'}
                    </span>
                </div>

                <div class="result-prob">{pct}%</div>
                <div style="color:#636363; font-size:13px; margin-bottom:16px;">
                    Predicted churn probability ·
                    decision threshold {threshold:.4f}
                </div>

                <div class="risk-band" style="position:relative;">
                    <i class="low"  style="width:40%"></i>
                    <i class="med"  style="width:30%"></i>
                    <i class="high" style="width:30%"></i>
                    <span style="position:absolute; top:-5px; left:{marker_pct}%;
                                 width:4px; height:20px; border-radius:2px;
                                 background:#202020; transform:translateX(-50%);
                                 outline:2px solid #FFFFFF;"></span>
                </div>

                <div style="display:flex; justify-content:space-between;
                            font-size:11px; color:#636363; margin-top:6px;">
                    <span>0% — Low</span>
                    <span>40% — Medium</span>
                    <span>70% — High</span>
                    <span>100%</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,     # ← REQUIRED
        )

    except Exception as e:
        st.error(f"Prediction failed: {e}")
        with st.expander("Details"):
            st.write("Customer ID:", cid_final)
            st.write("Features sent:", features)