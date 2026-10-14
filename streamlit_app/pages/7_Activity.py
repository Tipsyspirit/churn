import streamlit as st
from utils import session, styles, api
import pandas as pd

st.set_page_config(page_title="Activity · ChurnSight", layout="wide")
styles.inject()
session.init()
session.require_login()

st.title("Prediction history")

try:
    rows = api.history()
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        st.download_button("Download CSV", df.to_csv(index=False).encode(),
                          file_name="history.csv", mime="text/csv")
    else:
        st.info("No predictions yet.")
except Exception as e:
    st.error(str(e))