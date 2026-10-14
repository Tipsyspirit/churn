# Abstract

Customer churn is a critical business problem. This project presents ChurnSight,
a full-stack customer churn prediction system combining:

- An Extra Trees classifier trained on the E-Commerce Churn dataset (5,630 rows).
- A FastAPI backend that serves predictions and enforces JWT authentication.
- A Streamlit frontend for uploads, single predictions, retention tasks, and reporting.
- SQLite for users, prediction history, and audit logs.

The model achieves 97.34% accuracy, 91.67% precision, 92.63% recall, and
0.9963 ROC-AUC on a held-out test set, with a tuned classification threshold
of 0.4553.