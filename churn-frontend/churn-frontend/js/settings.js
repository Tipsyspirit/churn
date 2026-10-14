// Settings: sidebar with grouped sections. Every control here changes real behaviour in the app.
(function () {
  if (!window.App) return;
  var App = window.App, $ = App.$, esc = App.esc;
  var section = "prediction";
  var GROUPS = [
    ["Prediction & model", [["prediction", "Prediction settings"], ["model", "Model health"]]],
    ["Data", [["data", "Data management"]]],
    ["Alerts & retention", [["alerts", "Notifications"], ["retention", "Retention rules"]]],
    ["Organization", [["users", "Users & permissions"]]],
    ["Account", [["account", "Account & appearance"]]]
  ];
  var P = function () { return window.APP_PREFS; };
  function adminNote() { return App.can("settings") ? "" : '<p class="rnote">Only admins can change this. Switch the demo role under Users &amp; permissions.</p>'; }
  function dis(adminOnly) { return adminOnly && !App.can("settings") ? " disabled" : ""; }
  function tgl(id, on, text, sub, adminOnly) {
    return '<div class="sw-row"><div><b>' + text + "</b>" + (sub ? '<div class="sub">' + sub + "</div>" : "") + '</div><button class="tgl" id="' + id + '" role="switch" aria-checked="' + on + '" aria-label="' + text + '" type="button"' + dis(adminOnly) + "></button></div>";
  }
  function bindTgl(id, key, after) {
    var el = $(id); if (!el) return;
    el.addEventListener("click", function () {
      var on = el.getAttribute("aria-checked") !== "true"; el.setAttribute("aria-checked", String(on));
      App.setPref(key, on); if (after) after(on);
    });
  }

  // ---------- sections ----------
  var S = {};

  S.prediction = function (c) {
    var R = window.RISK, d = dis(true);
    c.innerHTML =
      '<form class="card light pop" id="setForm" novalidate><h3>Risk thresholds</h3>' + adminNote() +
      '<p class="sub">These categorize the model\'s predicted probability. They don\'t change the predictions themselves.</p>' +
      '<div class="fgrid"><label class="field2" for="s-low">Low risk below (%)<input class="inp" id="s-low" type="number" min="1" max="99" value="' + Math.round(R.lowBelow * 100) + '"' + d + '></label>' +
      '<label class="field2" for="s-high">High risk above (%)<input class="inp" id="s-high" type="number" min="1" max="99" value="' + Math.round(R.highAbove * 100) + '"' + d + "></label></div>" +
      '<div class="prev" id="prev" aria-live="polite"></div><div class="ferr" id="serr" role="alert"></div>' +
      '<div class="row"><button class="pbtn y" type="submit"' + d + '>Save thresholds</button><button class="pbtn" type="button" id="setReset"' + d + ">Reset to 40 / 70</button></div></form>" +
      '<article class="card light pop"><h3>Prediction behavior</h3>' + adminNote() +
      tgl("t-explain", P().explain, "Show reasons for predictions", "Lists the factors behind each customer's score.", false) +
      '<label class="field2" for="s-churnAt" style="margin-top:12px">Count a customer as "likely to churn" at<select class="inp" id="s-churnAt"' + d + ">" +
      [0.5, 0.6, 0.7].map(function (v) { return '<option value="' + v + '"' + (P().churnAt === v ? " selected" : "") + ">" + Math.round(v * 100) + "% or more</option>"; }).join("") + "</select></label>" +
      '<p class="sub">Used for the churn rate and for the Model page. Only one model is connected, so there is no model selector.</p></article>';
    function preview() {
      var lo = Number($("s-low").value) / 100, hi = Number($("s-high").value) / 100, ok = lo > 0 && hi < 1 && lo < hi, n = { low: 0, med: 0, high: 0 };
      if (App.list) App.list.forEach(function (x) { n[x.p < lo ? "low" : (x.p > hi ? "high" : "med")]++; });
      $("prev").innerHTML = ok ? '<span class="pill low">Low: below ' + Math.round(lo * 100) + "%" + (App.list ? " · " + n.low : "") + '</span><span class="pill med">Medium: ' + Math.round(lo * 100) + "–" + Math.round(hi * 100) + "%" + (App.list ? " · " + n.med : "") + '</span><span class="pill high">High: above ' + Math.round(hi * 100) + "%" + (App.list ? " · " + n.high : "") + "</span>" : '<span class="sub">Enter a low value that is smaller than the high value.</span>';
    }
    $("s-low").addEventListener("input", preview); $("s-high").addEventListener("input", preview); preview();
    $("setForm").addEventListener("submit", function (e) {
      e.preventDefault(); if (!App.can("settings")) return;
      var lo = Number($("s-low").value), hi = Number($("s-high").value);
      if (!(Number.isInteger(lo) && Number.isInteger(hi) && lo >= 1 && hi <= 99 && lo < hi)) { $("serr").textContent = "Use whole numbers from 1 to 99, with the low value smaller than the high value."; return; }
      $("serr").textContent = "";
      window.RISK = { lowBelow: lo / 100, highAbove: hi / 100 }; Store.set("settings", { low: lo / 100, high: hi / 100 });
      Store.audit("Changed risk thresholds", lo + "% / " + hi + "%"); App.recompute(); App.toast("Thresholds saved: low below " + lo + "%, high above " + hi + "%");
    });
    $("setReset").addEventListener("click", function () {
      window.RISK = { lowBelow: 0.4, highAbove: 0.7 }; Store.set("settings", { low: 0.4, high: 0.7 });
      Store.audit("Reset risk thresholds", "40% / 70%"); App.recompute(); render(); App.toast("Thresholds reset to 40% / 70%");
    });
    bindTgl("t-explain", "explain");
    $("s-churnAt").addEventListener("change", function (e) { App.setPref("churnAt", Number(e.target.value)); App.recompute(); App.toast("Churn decision threshold saved"); });
  };

  S.model = function (c) {
    var I = window.MODEL_INFO || {}, m = App.list ? Data.metrics(App.list) : null, live = !!window.PREDICT_URL;
    c.innerHTML = '<article class="card dark pop"><div class="rep-head"><h3>Model health</h3><span class="pill ' + (live ? "low" : "med") + '">' + (live ? "Connected" : "Placeholder, not deployed") + "</span></div>" +
      '<dl class="about"><dt>Active model</dt><dd>' + esc(I.name || "") + "</dd><dt>Version</dt><dd>" + esc(I.version || "") + "</dd><dt>Last trained</dt><dd>" + esc(I.trained || "") + "</dd><dt>Endpoint</dt><dd>" + (live ? esc(window.PREDICT_URL) : "None. Using the demo formula in js/data.js") + "</dd></dl></article>" +
      '<article class="card light pop"><h3>Latest evaluation</h3>' + (m && !m.onlyOneClass ?
        '<div class="sumrow2"><div><b class="mono">' + (m.accuracy * 100).toFixed(1) + '%</b><span>Accuracy</span></div><div><b class="mono">' + (m.precision * 100).toFixed(1) + '%</b><span>Precision</span></div><div><b class="mono">' + (m.recall * 100).toFixed(1) + '%</b><span>Recall</span></div><div><b class="mono">' + m.f1.toFixed(2) + '</b><span>F1</span></div><div><b class="mono">' + m.auc.toFixed(2) + "</b><span>ROC-AUC</span></div></div>"
        : '<p class="sub" style="margin-top:6px">' + (App.list ? "Add a churned column (0/1) to your CSV to see evaluation metrics." : "Upload a dataset to see evaluation metrics.") + "</p>") +
      '<div class="row" style="margin-top:12px"><button class="pbtn" type="button" data-go="model">Open the Model page →</button></div></article>';
  };

  S.data = function (c) {
    var ds = Store.get("dataset", null), r = App.report, rows = ds ? ds.customers : null;
    var labelled = rows ? rows.filter(function (x) { return x.actual === 0 || x.actual === 1; }).length : 0;
    c.innerHTML = '<article class="card light pop"><h3>Dataset</h3>' + (ds ?
      '<dl class="about light"><dt>File</dt><dd>' + esc(ds.name) + "</dd><dt>Rows used</dt><dd>" + rows.length.toLocaleString("en-IN") + "</dd><dt>Rows skipped</dt><dd>" + (r ? r.failed : 0) + "</dd><dt>Outcome labels</dt><dd>" + (labelled ? labelled + " customers have a churned value" : "None. Evaluation is unavailable") + "</dd><dt>Uploaded</dt><dd>" + App.fmtDate(ds.ts) + "</dd></dl>" +
      '<p class="sub">Every upload is checked for wrong column counts, non-numbers, out-of-range values and duplicate customer IDs. Blank numbers are filled with the column median. Skipped rows are listed in the Upload report on Home.</p>' +
      '<div class="row"><button class="pbtn y" type="button" data-act="goUpload"' + (App.can("write") ? "" : " disabled") + '>Upload new dataset</button><button class="pbtn" type="button" id="dExport">⬇ Export predictions</button></div>'
      : '<p class="sub" style="margin-top:6px">No dataset saved yet.</p><div class="row"><button class="pbtn y" type="button" data-act="goUpload">Upload a dataset</button></div>') + "</article>" +
      '<article class="card light pop danger"><h3>Clear saved data</h3>' + adminNote() +
      '<p class="sub">Deletes the dataset, prediction history, retention tasks and audit log stored in this browser. Your settings and sign-in stay. This cannot be undone.</p>' +
      '<div class="row"><button class="pbtn bad" type="button" id="wipe"' + dis(true) + ">Clear all saved data</button></div></article>";
    var ex = $("dExport"); if (ex) ex.addEventListener("click", function () { App.download("churn_predictions.csv", Data.toCSV(App.list)); Store.audit("Exported predictions", App.list.length + " rows"); });
    $("wipe").addEventListener("click", function () {
      var w = $("wipe"); if (w.dataset.sure !== "1") { w.dataset.sure = "1"; w.textContent = "Click again to confirm"; return; }
      Store.audit("Cleared all saved data", ""); ["dataset", "history", "tasks"].forEach(Store.del); Store.set("audit", []); location.hash = "#home"; location.reload();
    });
  };

  S.alerts = function (c) {
    c.innerHTML = '<article class="card light pop"><h3>Notifications</h3><p class="sub">Alerts appear in the app after you upload a dataset. Email alerts need a backend.</p>' +
      tgl("t-nh", P().notifyHigh, "High-risk customers found", "Shows how many high-risk customers an upload contains.", false) +
      tgl("t-nf", P().notifyFail, "Rows failed validation", "Warns when rows in a file couldn't be used.", false) + "</article>";
    bindTgl("t-nh", "notifyHigh"); bindTgl("t-nf", "notifyFail");
  };

  S.retention = function (c) {
    var d = dis(true);
    c.innerHTML = '<article class="card light pop"><h3>Retention rules</h3>' + adminNote() +
      '<p class="sub">These rules apply to the Retention page. Tasks are assigned by hand there.</p>' +
      tgl("t-auto", P().autoTasks, "Create follow-up tasks automatically", "After each upload, add a task for every high-risk customer who has no open task.", true) +
      '<div class="fgrid"><label class="field2" for="s-dh">Follow-up for high risk (days)<input class="inp" id="s-dh" type="number" min="1" max="60" value="' + P().dueHigh + '"' + d + '></label>' +
      '<label class="field2" for="s-dm">Follow-up for medium risk (days)<input class="inp" id="s-dm" type="number" min="1" max="60" value="' + P().dueMed + '"' + d + "></label></div>" +
      '<div class="ferr" id="rerr" role="alert"></div><div class="row"><button class="pbtn y" type="button" id="rSave"' + d + ">Save follow-up days</button></div></article>";
    bindTgl("t-auto", "autoTasks");
    $("rSave").addEventListener("click", function () {
      var h = Number($("s-dh").value), m = Number($("s-dm").value);
      if (!(Number.isInteger(h) && Number.isInteger(m) && h >= 1 && m >= 1 && h <= 60 && m <= 60)) { $("rerr").textContent = "Use whole numbers from 1 to 60."; return; }
      $("rerr").textContent = ""; App.setPref("dueHigh", h, true); App.setPref("dueMed", m, true); Store.audit("Changed follow-up days", h + " / " + m); App.toast("Follow-up days saved");
    });
  };

  S.users = function (c) {
    var u = App.user;
    c.innerHTML = '<article class="card light pop"><h3>Your role</h3><p class="sub">Signed in as <b>' + esc(u.name || "") + "</b> (" + esc(u.email || "") + ").</p>" +
      '<label class="field2" for="s-role">Demo role<select class="inp" id="s-role">' + Auth.ROLES.map(function (r) { return '<option value="' + r + '"' + (u.role === r ? " selected" : "") + ">" + r + "</option>"; }).join("") + "</select></label>" +
      '<p class="sub">Switching roles here is for demonstration. In a real deployment, permissions must be enforced on the server, not by a dropdown in the browser.</p></article>' +
      '<article class="card light pop"><h3>What each role can do</h3><div class="tbl-wrap"><table style="min-width:420px"><thead><tr><th>Role</th><th>Access</th></tr></thead><tbody>' +
      '<tr><td><b>Viewer</b></td><td>View dashboards, customers and prediction results</td></tr><tr><td><b>Analyst</b></td><td>Upload data, run predictions and manage retention tasks</td></tr><tr><td><b>Admin</b></td><td>Everything above, plus settings and the audit log</td></tr></tbody></table></div></article>';
    $("s-role").addEventListener("change", function (e) {
      var cur = Auth.getUser(); cur.role = e.target.value; Auth.setUser(cur); Store.audit("Changed demo role", cur.role);
      App.refreshRole(); render(); App.toast("Role is now " + cur.role);
    });
  };

  S.account = function (c) {
    var u = App.user;
    c.innerHTML = '<article class="card light pop"><h3>Profile</h3><dl class="about light"><dt>Name</dt><dd>' + esc(u.name || "") + "</dd><dt>Email</dt><dd>" + esc(u.email || "") + "</dd><dt>Sign-in</dt><dd>" + (u.google ? "Google" : "Demo email login") + "</dd><dt>Role</dt><dd>" + esc(u.role) + "</dd></dl>" +
      '<div class="row"><button class="pbtn" type="button" id="sOut">Sign out</button></div></article>' +
      '<article class="card light pop"><h3>Appearance</h3><label class="field2" for="s-theme">Theme<select class="inp" id="s-theme"><option value="light"' + (Theme.get() === "light" ? " selected" : "") + '>Light</option><option value="dark"' + (Theme.get() === "dark" ? " selected" : "") + '>Dark</option></select></label><label class="field2" for="s-den" style="margin-top:12px">Table density<select class="inp" id="s-den"><option value="comfortable"' + (P().density === "comfortable" ? " selected" : "") + ">Comfortable</option><option value=\"compact\"" + (P().density === "compact" ? " selected" : "") + ">Compact (more rows on screen)</option></select></label></article>";
    $("sOut").addEventListener("click", Auth.signOut);
    $("s-theme").addEventListener("change", function (e) { Theme.set(e.target.value); });
    $("s-den").addEventListener("change", function (e) { App.setPref("density", e.target.value); App.toast("Table density: " + e.target.value); });
  };

  // ---------- page shell ----------
  function render() {
    var nav = GROUPS.map(function (g) {
      return '<div class="sn-group"><div class="sn-h">' + g[0] + "</div>" + g[1].map(function (i) {
        return '<button type="button" class="sn-i" data-s="' + i[0] + '"' + (i[0] === section ? ' aria-current="page"' : "") + ">" + i[1] + "</button>";
      }).join("") + "</div>";
    }).join("");
    var b = $("body-settings");
    b.innerHTML = '<div class="set-wrap"><nav class="set-nav" aria-label="Settings sections">' + nav + '</nav><div class="set-body" id="setBody"></div></div>';
    b.querySelector(".set-nav").addEventListener("click", function (e) { var i = e.target.closest(".sn-i"); if (i) { section = i.dataset.s; render(); } });
    S[section]($("setBody")); App.popIn($("setBody"));
  }
  window.addEventListener("themechange", function () { var t = document.getElementById("s-theme"); if (t) t.value = Theme.get(); });
  App.views.settings = { render: render };
  // Settings are opened from the profile menu: App.openSettings("retention") etc.
  App.openSettings = function (name) { if (S[name]) section = name; App.show("settings"); };
})();
