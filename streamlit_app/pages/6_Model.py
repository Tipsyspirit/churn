import streamlit as st
from utils import session, styles, api

st.set_page_config(page_title="Model · ChurnSight", layout="wide")
styles.inject()
session.init()

st.title("Model information")

st.markdown("""
### Extra Trees Classifier
- **Algorithm:** ExtraTreesClassifier (balanced class weights)
- **Features:** 13 numeric + 5 categorical (one-hot encoded)
- **Training set:** 5,630 customers · E Commerce Dataset
- **Threshold:** 0.4553 (tuned on validation set to maximize F1)

### Test set performance
| Metric | Score |
|--------|-------|
| Accuracy | 97.34% |
| Precision | 91.67% |
| Recall | 92.63% |
| F1-score | 0.9215 |
| ROC-AUC | 0.9963 |

### Top churn drivers
1. Tenure (24.99%)
2. Cashback Amount (9.31%)
3. Complain (6.54%)
4. Warehouse to Home (6.01%)

### Limitations
Trained on e-commerce customer data. Not validated for other industries.
""")

h = api.health()
st.json(h)