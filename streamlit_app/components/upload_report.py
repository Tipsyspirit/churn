import streamlit as st

def show(report: dict):
    st.subheader("Upload report")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows in file", report.get("total", 0))
    c2.metric("Valid rows", report.get("valid", 0))
    c3.metric("Failed rows", report.get("failed", 0))
    errors = report.get("errors", [])
    if errors:
        with st.expander("Rows that failed validation"):
            for err in errors[:50]:
                st.write(f"Row {err['row']}: {err['msg']}")