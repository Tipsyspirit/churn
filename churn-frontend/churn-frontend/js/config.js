// Project settings. Edit this file, not the other scripts.

// 1) Google sign-in. Paste your OAuth "Web application" client ID here, or paste it into the box on the
//    login page (that saves it in your browser). Steps are in README.md.
window.GOOGLE_CLIENT_ID = "";

// 2) Default risk bands. Admins can change them in Settings. P3 owns the matching retention rules.
window.RISK = { lowBelow: 0.40, highAbove: 0.70 };

// 3) When P1's model is served by a backend, set the URL, e.g. "http://localhost:8000/predict".
//    Leave empty to use the demo scoring formula in js/data.js.
window.PREDICT_URL = "";

// 4) Shown on the Model page. Update these when the real model is connected.
window.MODEL_INFO = {
  name: "Demo scoring formula",
  algorithm: "Hand-set logistic formula (placeholder, not trained)",
  version: "demo-0.1",
  trained: "Not trained. Connect your model to replace this.",
  dataset: "Whatever CSV you upload",
  limits: "Reasons and probabilities come from a placeholder formula, so they are for demonstration only."
};
