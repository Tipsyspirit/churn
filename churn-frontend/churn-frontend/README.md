# ChurnSight frontend

Static HTML/CSS/JS, no build step.

## Run it
    cd churn-frontend
    python -m http.server 8000      # then open http://localhost:8000
Everything except Google sign-in also works if you double-click index.html. Google sign-in needs the http://localhost address.

## Pages
| Page | What it does | File |
|---|---|---|
| Landing | Marketing page (light, reference 1) | index.html |
| Login | Google (redirects to Google's page) + demo email login with a role | login.html |
| Home | KPI cards, charts, upload report, top at-risk table | dashboard.html, js/dashboard.js |
| Customers | Search, risk filter, sort, pagination, click a row for the prediction + reasons | js/views.js |
| Predict | Manual prediction form, pick an existing customer, bulk upload shortcut | js/views.js |
| Retention | Tasks: assignee, follow-up date, status (To contact / Contacted / Retained / Churned) | js/views.js |
| Report | Revenue statement report (income-statement style): totals by risk, revenue by tenure, high-risk revenue by recency, assistant summary, save as CSV | js/report.js |
| Model | About the model, what drives churn, accuracy / precision / recall / F1 / AUC, confusion matrix, ROC | js/views.js |
| Activity | Prediction history (export CSV) and the audit log (admin only) | js/views.js |
| Settings (opened from the profile menu, no navbar tab) | Sidebar sections: prediction (thresholds with live preview, reasons on/off, churn decision threshold), model health, data management, notifications, retention rules, users & permissions, account & appearance | js/settings.js |

## Files
- js/config.js: Google client ID, default risk bands, PREDICT_URL, MODEL_INFO text
- js/data.js: CSV parsing + row validation, scoring, reasons, metrics (shared with the ML person)
- js/store.js: browser storage for dataset, history, tasks, audit log
- js/auth.js: session + roles
- js/sample.js and sample_customers.csv: 200 made-up customers (same data)

## Google sign-in
1. console.cloud.google.com -> APIs & Services -> OAuth consent screen (External; add your Google account as a test user).
2. Credentials -> Create credentials -> OAuth client ID -> Web application.
3. Authorized redirect URIs: http://localhost:8000/login.html (exact). Add your deployed login.html URL later.
4. Click "Continue with Google" on the login page and paste the Client ID in the box (saved in your browser), or set window.GOOGLE_CLIENT_ID in js/config.js.
The browser then goes to Google's sign-in page and returns to login.html. The token is only decoded to show your name; verify it on your backend before trusting it.

## Connect the real model
Demo scoring is demoScore() in js/data.js. Set PREDICT_URL in js/config.js.
Request: POST a JSON array of {id, tenure, orders, days, tickets, aov, discount}
Response: JSON array of {id, churn_probability} (0..1)
Update MODEL_INFO in js/config.js (name, algorithm, version, trained date, limitations).
The "reasons" shown per customer and the "What drives churn" chart currently come from the demo formula. Replace Data.explain / Data.importance with output from your model (for example feature importances or SHAP values).

## CSV format
customer_id, tenure_months, orders_90d, days_since_last_order, support_tickets, avg_order_value, discount_use_pct, churned (optional, 0/1)
Rows that can't be used (wrong column count, non-numeric or out-of-range values, duplicate IDs) are listed in the Upload report, never silently dropped. Blank numbers are filled with the column median and counted.

## Not included (needs a backend)
Real authentication and role enforcement, a database (data lives in this browser), PDF reports, model performance over time, and a trained model.

## Report page note
Revenue is estimated per customer as avg order value x orders in 90 days / 3. It is a revenue estimate from your customer file, not an accounting income statement (the file has no expense data).

## Settings that change behaviour
reasons on/off, churn decision threshold (50/60/70%), risk thresholds, in-app alerts after upload, automatic follow-up tasks, follow-up days, table density. Settings are stored in this browser.

## Theme (light / dark)
Light mode uses the design palette: page #7D7D7D, cards #FFFFFF, navbar #1D1D1D, primary buttons #F5EE50, card text #202020, page text #FFFFFF. Dark mode is derived from it (page #121212, cards #1F1F1F, navbar #0A0A0A, same yellow). All colors live in `css/theme.css`; `js/theme.js` handles the toggle (landing nav, login, profile menu, Settings > Account & appearance) and remembers the choice. Note: white text on #7D7D7D is about 4.1:1 contrast; #767676 would pass WCAG AA.

## Profile menu
Click the avatar: Upload new dataset, every Settings section (opens Settings at that section), Dark mode switch, Sign out.
