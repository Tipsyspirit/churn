// Pages other than Home: Customers, Predict, Retention, Model, Activity, Settings, and the customer drawer.
(function () {
  if (!window.App) return;
  var App = window.App, $ = App.$, esc = App.esc;
  var LAB = { high: "High", med: "Medium", low: "Low" };
  function pill(r) { return '<span class="pill ' + r + '">' + LAB[r] + "</span>"; }
  function pct(p) { return Math.round(p * 100); }
  function today() { return new Date().toISOString().slice(0, 10); }
  function addDays(n) { var d = new Date(); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10); }
  function noData(what) {
    return '<div class="card light empty pop"><h3>No dataset yet</h3><p>' + what + '</p><button class="pbtn y" type="button" data-act="goUpload">Upload a dataset</button></div>';
  }
  function body(name, html) { var b = $("body-" + name); b.innerHTML = html; App.popIn(b); return b; }
  function readOnlyNote() { return App.can("write") ? "" : '<p class="rnote">Your role is read-only (viewer). You can look, but not change anything.</p>'; }

  // =================== Prediction result (shared by Predict page and the drawer) ===================
  function resultHTML(c) {
    var r = Data.riskOf(c.p), p = pct(c.p), ex = Data.explain(c, App.means), R = window.RISK;
    var likely = c.p >= Data.CHURN_AT;
    function factors(list, cls) {
      return list.slice(0, 3).map(function (f) { return '<li><span>' + esc(f.text) + '</span><i class="fbar ' + cls + '"><b style="width:' + Math.max(12, Math.round(f.share * 100)) + '%"></b></i></li>'; }).join("");
    }
    return '<div class="res">' +
      '<div class="eyebrow-d">Prediction result</div><h2 class="res-id">' + esc(c.id) + "</h2>" +
      '<div class="res-top">' + pill(r) + '<span class="outcome ' + (likely ? "bad" : "ok") + '">' + (likely ? "Likely to churn" : "Likely to stay") + "</span></div>" +
      '<div class="res-p mono">' + p + '%</div><div class="sub">Predicted churn probability · ' + new Date().toLocaleDateString("en-IN", { dateStyle: "medium" }) + "</div>" +
      '<div class="band" aria-hidden="true"><i class="low" style="width:' + R.lowBelow * 100 + '%"></i><i class="med" style="width:' + (R.highAbove - R.lowBelow) * 100 + '%"></i><i class="high" style="width:' + (100 - R.highAbove * 100) + '%"></i><span class="mk" style="left:' + p + '%"></span></div>' +
      (window.APP_PREFS.explain ? '<h4>Factors raising the risk</h4>' + (ex.up.length ? '<ul class="factors">' + factors(ex.up, "up") + "</ul>" : '<p class="sub">Nothing stands out compared with the average customer.</p>') +
      (ex.down.length ? '<h4>Factors keeping this customer</h4><ul class="factors">' + factors(ex.down, "down") + "</ul>" : "") : "") +
      '<div class="action a-' + r + '"><b>Suggested next step</b><br>' + Data.NEXT[r] + "</div>" +
      (window.PREDICT_URL ? "" : '<p class="sub" style="margin-top:10px">Factors come from the placeholder scoring formula. They are for demonstration until your trained model is connected.</p>') +
      "</div>";
  }

  // =================== Drawer ===================
  var lastFocus = null;
  App.openDrawer = function (c) {
    lastFocus = document.activeElement;
    var tasks = Store.get("tasks", []), has = tasks.some(function (t) { return t.customer === c.id && t.status !== "Retained" && t.status !== "Churned"; });
    $("drawerBody").innerHTML = resultHTML(c) +
      '<div class="res-actions"><button class="pbtn y" type="button" id="mkTask"' + (has || !App.can("write") ? " disabled" : "") + ">" + (has ? "Task already open" : "Create retention task") + "</button></div>";
    $("drawer").hidden = false; document.body.style.overflow = "hidden";
    var p = $("drawer").querySelector(".drawer-panel"); p.classList.remove("in"); void p.offsetWidth; p.classList.add("in");
    $("drawerX").focus();
    var b = $("mkTask"); if (b) b.addEventListener("click", function () { if (createTask(c)) { b.disabled = true; b.textContent = "Task created"; } });
  };
  function closeDrawer() { $("drawer").hidden = true; document.body.style.overflow = ""; if (lastFocus && lastFocus.focus) lastFocus.focus(); }
  $("drawerX").addEventListener("click", closeDrawer);
  $("drawerBg").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !$("drawer").hidden) closeDrawer(); });

  // =================== Customers ===================
  var cs = { q: "", risk: "all", key: "p", dir: -1, page: 1, size: 10 };
  var COLS = [["id", "Customer"], ["tenure", "Tenure (mo)"], ["orders", "Orders 90d"], ["days", "Days since order"], ["tickets", "Tickets"], ["aov", "Avg order"], ["discount", "Discount %"], ["p", "Churn risk"]];
  function custRows() {
    var q = cs.q.trim().toLowerCase();
    var list = App.list.filter(function (c) { return (cs.risk === "all" || Data.riskOf(c.p) === cs.risk) && (!q || String(c.id).toLowerCase().indexOf(q) >= 0); });
    list.sort(function (a, b) {
      var x = a[cs.key], y = b[cs.key];
      if (cs.key === "id") return cs.dir * String(x).localeCompare(String(y), undefined, { numeric: true });
      return cs.dir * (x - y);
    });
    return list;
  }
  function custUpdate() {
    var list = custRows(), pages = Math.max(1, Math.ceil(list.length / cs.size));
    if (cs.page > pages) cs.page = pages;
    var from = (cs.page - 1) * cs.size, slice = list.slice(from, from + cs.size);
    $("custHead").innerHTML = "<tr>" + COLS.map(function (c) {
      var on = cs.key === c[0];
      return '<th aria-sort="' + (on ? (cs.dir > 0 ? "ascending" : "descending") : "none") + '"><button type="button" class="sortbtn" data-k="' + c[0] + '">' + c[1] + (on ? (cs.dir > 0 ? " ▲" : " ▼") : "") + "</button></th>";
    }).join("") + "<th>Status</th></tr>";
    $("custRows").innerHTML = slice.length ? slice.map(function (c) {
      var r = Data.riskOf(c.p);
      return '<tr tabindex="0" data-id="' + esc(c.id) + '"><td class="mono"><b>' + esc(c.id) + '</b></td><td class="mono">' + Math.round(c.tenure) + '</td><td class="mono">' + Math.round(c.orders) + '</td><td class="mono">' + Math.round(c.days) +
        '</td><td class="mono">' + Math.round(c.tickets) + '</td><td class="mono">' + App.inr(c.aov) + '</td><td class="mono">' + Math.round(c.discount) + '%</td>' +
        '<td class="mono"><span class="meter"><b class="' + r + '" style="width:' + pct(c.p) + '%"></b></span>' + pct(c.p) + "%</td><td>" + pill(r) + "</td></tr>";
    }).join("") : '<tr><td colspan="9" class="sub" style="padding:24px;text-align:center">No customers match your search.</td></tr>';
    $("custInfo").textContent = list.length ? "Showing " + (from + 1) + "–" + (from + slice.length) + " of " + list.length.toLocaleString("en-IN") : "0 customers";
    $("pgPrev").disabled = cs.page <= 1; $("pgNext").disabled = cs.page >= pages; $("pgNum").textContent = "Page " + cs.page + " of " + pages;
  }
  App.views.customers = {
    render: function () {
      if (!App.list) return void body("customers", noData("Upload a customer file to browse and search every customer."));
      var chips = [["all", "All"], ["high", "High"], ["med", "Medium"], ["low", "Low"]].map(function (c) {
        return '<button class="chip" type="button" data-r="' + c[0] + '" aria-pressed="' + (cs.risk === c[0]) + '">' + c[1] + "</button>";
      }).join("");
      var b = body("customers",
        '<div class="card light pop"><div class="tools"><label class="sr" for="custQ">Search customers</label><input class="inp" id="custQ" type="search" placeholder="Search by customer ID" value="' + esc(cs.q) + '"><div class="chips" role="group" aria-label="Filter by risk">' + chips + '</div><span class="sub" id="custInfo" style="margin-left:auto"></span></div>' +
        '<div class="tbl-wrap"><table class="big"><thead id="custHead"></thead><tbody id="custRows"></tbody></table></div>' +
        '<div class="pager"><button class="pbtn" type="button" id="pgPrev">← Previous</button><span class="sub" id="pgNum"></span><button class="pbtn" type="button" id="pgNext">Next →</button></div></div>');
      $("custQ").addEventListener("input", function (e) { cs.q = e.target.value; cs.page = 1; custUpdate(); });
      b.querySelectorAll(".chip").forEach(function (ch) { ch.addEventListener("click", function () {
        cs.risk = ch.dataset.r; cs.page = 1; b.querySelectorAll(".chip").forEach(function (x) { x.setAttribute("aria-pressed", String(x === ch)); }); custUpdate(); }); });
      $("custHead").addEventListener("click", function (e) {
        var s = e.target.closest(".sortbtn"); if (!s) return;
        if (cs.key === s.dataset.k) cs.dir = -cs.dir; else { cs.key = s.dataset.k; cs.dir = s.dataset.k === "id" ? 1 : -1; }
        custUpdate();
      });
      function open(e) { var tr = e.target.closest("tr[data-id]"); if (!tr) return; var c = App.list.filter(function (x) { return String(x.id) === tr.dataset.id; })[0]; if (c) App.openDrawer(c); }
      $("custRows").addEventListener("click", open);
      $("custRows").addEventListener("keydown", function (e) { if (e.key === "Enter") open(e); });
      $("pgPrev").addEventListener("click", function () { cs.page--; custUpdate(); });
      $("pgNext").addEventListener("click", function () { cs.page++; custUpdate(); });
      custUpdate();
    }
  };

  // =================== Predict (manual) ===================
  var FIELDS = [
    ["tenure", "Tenure (months)", 12, 0, 600], ["orders", "Orders in last 90 days", 3, 0, 500], ["days", "Days since last order", 30, 0, 3650],
    ["tickets", "Support tickets", 0, 0, 500], ["aov", "Average order value (₹)", 1500, 0, 10000000], ["discount", "Discount use (%)", 20, 0, 100]
  ];
  var manualN = 0;
  App.views.predict = {
    render: function () {
      var opts = App.list ? '<label class="field2" for="pickCust">Or pick an existing customer<select class="inp" id="pickCust"><option value="">Select a customer…</option>' +
        App.list.slice().sort(function (a, b) { return b.p - a.p; }).slice(0, 200).map(function (c) { return '<option value="' + esc(c.id) + '">' + esc(c.id) + " · " + pct(c.p) + "%</option>"; }).join("") + "</select></label>" : "";
      var fields = FIELDS.map(function (f) {
        return '<label class="field2" for="f-' + f[0] + '">' + f[1] + '<input class="inp" id="f-' + f[0] + '" type="number" inputmode="decimal" min="' + f[3] + '" max="' + f[4] + '" step="any" value="' + f[2] + '" required></label>';
      }).join("");
      var b = body("predict",
        '<div class="grid2"><form class="card light pop" id="predForm" novalidate>' + readOnlyNote() + '<h3>Customer details</h3>' +
        '<label class="field2" for="f-id">Customer ID (optional)<input class="inp" id="f-id" placeholder="e.g. C-2048" autocomplete="off"></label>' + opts +
        '<div class="fgrid">' + fields + '</div><div class="ferr" id="ferr" role="alert"></div>' +
        '<div class="row"><button class="pbtn y" type="submit">Predict churn</button>' +
        '<button class="pbtn" type="button" data-act="goUpload">Upload CSV for bulk prediction</button></div></form>' +
        '<div class="card light pop" id="predOut"><div class="empty-in"><h3>Result</h3><p class="sub">Fill in the details and press <b>Predict churn</b>. The probability, risk category and reasons appear here.</p></div></div></div>');
      var pick = $("pickCust");
      if (pick) pick.addEventListener("change", function () {
        var c = App.list.filter(function (x) { return String(x.id) === pick.value; })[0]; if (!c) return;
        $("f-id").value = c.id; FIELDS.forEach(function (f) { $("f-" + f[0]).value = Math.round(c[f[0]]); });
      });
      $("predForm").addEventListener("submit", function (e) {
        e.preventDefault();
        var c = { id: $("f-id").value.trim() }, bad = "";
        FIELDS.forEach(function (f) {
          var el = $("f-" + f[0]), raw = el.value.trim(), n = Number(raw);
          if (raw === "" || !isFinite(n)) bad = bad || f[1] + " needs a number.";
          else if (n < f[3] || n > f[4]) bad = bad || f[1] + " must be between " + f[3] + " and " + f[4] + ".";
          c[f[0]] = n;
        });
        $("ferr").textContent = bad; if (bad) return;
        if (!c.id) c.id = "Manual-" + (++manualN);
        Data.predict([c]).then(function (out) {
          var r = out[0], o = $("predOut"); o.innerHTML = resultHTML(r) +
            '<div class="res-actions"><button class="pbtn" type="button" id="mkTask2"' + (App.can("write") ? "" : " disabled") + ">Create retention task</button></div>";
          App.popIn(o.parentNode);
          if (App.can("write")) {
            Store.addHistory({ type: "manual", customer: r.id, p: r.p, risk: Data.riskOf(r.p) });
            Store.audit("Manual prediction", r.id + " · " + pct(r.p) + "%");
          }
          $("mkTask2").addEventListener("click", function () { if (createTask(r)) { $("mkTask2").disabled = true; $("mkTask2").textContent = "Task created"; } });
        }).catch(function (err) { $("ferr").textContent = "Prediction failed: " + err.message; });
      });
    }
  };

  // =================== Retention tasks ===================
  var STATUSES = ["To contact", "Contacted", "Retained", "Churned"];
  function tasks() { return Store.get("tasks", []); }
  function createTask(c, quiet) {
    if (!App.can("write")) { App.toast("Your role is read-only"); return false; }
    var t = tasks();
    if (t.some(function (x) { return x.customer === c.id && x.status !== "Retained" && x.status !== "Churned"; })) { if (!quiet) App.toast("An open task already exists for " + c.id); return false; }
    var r = Data.riskOf(c.p);
    t.unshift({ id: "T" + Date.now().toString(36) + Math.random().toString(36).slice(2, 5), customer: c.id, p: c.p, risk: r, action: Data.ACTIONS[r], assignee: "", due: addDays(r === "high" ? window.APP_PREFS.dueHigh : window.APP_PREFS.dueMed), status: "To contact", created: Date.now() });
    Store.set("tasks", t);
    if (!quiet) { Store.audit("Created retention task", c.id); App.toast("Task created for " + c.id); }
    return true;
  }
  function retRender() {
    var t = tasks(), canW = App.can("write"), dis = canW ? "" : " disabled";
    var cnt = {}; STATUSES.forEach(function (s) { cnt[s] = t.filter(function (x) { return x.status === s; }).length; });
    var high = App.list ? App.list.filter(function (c) { return Data.riskOf(c.p) === "high"; }) : [];
    var open = {}; t.forEach(function (x) { if (x.status !== "Retained" && x.status !== "Churned") open[x.customer] = 1; });
    var pending = high.filter(function (c) { return !open[c.id]; });
    var done = cnt.Retained + cnt.Churned, saved = done ? Math.round(cnt.Retained / done * 100) : null;
    var rows = t.map(function (x) {
      var overdue = x.due < today() && (x.status === "To contact" || x.status === "Contacted");
      return '<tr data-id="' + x.id + '"><td><b>' + esc(x.customer) + '</b><div class="sub">' + pct(x.p) + "% · " + pill(x.risk) + "</div></td><td>" + esc(x.action) + "</td>" +
        '<td><input class="inp sm" data-f="assignee" aria-label="Assignee for ' + esc(x.customer) + '" placeholder="Team member" value="' + esc(x.assignee) + '"' + dis + "></td>" +
        '<td><input class="inp sm" type="date" data-f="due" aria-label="Follow-up date for ' + esc(x.customer) + '" value="' + x.due + '"' + dis + (overdue ? ' style="border-color:var(--high)"' : "") + ">" + (overdue ? '<div class="sub" style="color:var(--high);font-weight:600">Overdue</div>' : "") + "</td>" +
        '<td><select class="inp sm st-' + x.status.replace(" ", "") + '" data-f="status" aria-label="Status for ' + esc(x.customer) + '"' + dis + ">" + STATUSES.map(function (s) { return "<option" + (s === x.status ? " selected" : "") + ">" + s + "</option>"; }).join("") + "</select></td>" +
        '<td><button class="eye" type="button" data-del="1" aria-label="Delete task for ' + esc(x.customer) + '"' + dis + ">✕</button></td></tr>";
    }).join("");
    var b = body("retention", readOnlyNote() +
      '<div class="grid2 g-tasks"><article class="card dark pop"><h3>Task summary</h3><div class="sumrow">' + STATUSES.map(function (s) { return '<div><b class="mono">' + cnt[s] + "</b><span>" + s + "</span></div>"; }).join("") + "</div>" +
      '<p class="sub" style="margin-top:12px">' + (saved == null ? "Mark tasks Retained or Churned to track how many customers you kept." : "Retention rate so far: <b style='color:var(--y)'>" + saved + "%</b> of closed tasks stayed.") + "</p></article>" +
      '<article class="card light pop"><h3>Create tasks</h3>' + (App.list ?
        '<p class="sub">' + pending.length + " high-risk customer" + (pending.length === 1 ? "" : "s") + " without an open task.</p><div class=\"row\"><button class=\"pbtn y\" type=\"button\" id=\"bulkTasks\"" + (pending.length && canW ? "" : " disabled") + ">Create tasks for all high-risk</button></div>" +
        '<div class="row" style="margin-top:10px"><input class="inp" id="taskCust" list="custList" placeholder="Customer ID" aria-label="Customer ID"><datalist id="custList">' + App.list.slice().sort(function (a, b) { return b.p - a.p; }).slice(0, 200).map(function (c) { return '<option value="' + esc(c.id) + '">'; }).join("") + '</datalist><button class="pbtn" type="button" id="addTask"' + dis + ">Add task</button></div>"
        : '<p class="sub">Upload a dataset to create tasks from predictions.</p><button class="pbtn y" type="button" data-act="goUpload">Upload a dataset</button>') + "</article></div>" +
      '<article class="card light pop" style="margin-top:12px"><h3>Follow-ups</h3>' + (t.length ?
        '<div class="tbl-wrap"><table class="big"><thead><tr><th>Customer</th><th>Action</th><th>Assigned to</th><th>Follow-up date</th><th>Status</th><th></th></tr></thead><tbody id="taskRows">' + rows + "</tbody></table></div>"
        : '<p class="sub" style="margin-top:8px">No tasks yet. Create one from a customer\'s prediction, or add all high-risk customers at once.</p>') + "</article>");
    var bt = $("bulkTasks"); if (bt) bt.addEventListener("click", function () {
      var n = 0; pending.forEach(function (c) { if (createTask(c, true)) n++; });
      Store.audit("Created retention tasks", n + " high-risk customers"); App.toast(n + " tasks created"); retRender();
    });
    var at = $("addTask"); if (at) at.addEventListener("click", function () {
      var id = $("taskCust").value.trim(), c = App.list.filter(function (x) { return String(x.id) === id; })[0];
      if (!c) return App.toast("Pick a customer ID from the dataset"); if (createTask(c)) retRender();
    });
    var tr = $("taskRows"); if (tr) {
      tr.addEventListener("change", function (e) {
        var row = e.target.closest("tr"), f = e.target.dataset.f; if (!row || !f) return;
        var all = tasks(), x = all.filter(function (y) { return y.id === row.dataset.id; })[0]; if (!x) return;
        x[f] = e.target.value; Store.set("tasks", all);
        Store.audit("Updated retention task", x.customer + " · " + f + " → " + e.target.value);
        if (f === "status") retRender();
      });
      tr.addEventListener("click", function (e) {
        var d = e.target.closest("[data-del]"); if (!d) return;
        var id = d.closest("tr").dataset.id, all = tasks(), x = all.filter(function (y) { return y.id === id; })[0];
        Store.set("tasks", all.filter(function (y) { return y.id !== id; })); Store.audit("Deleted retention task", x ? x.customer : id); retRender();
      });
    }
  }
  App.views.retention = { render: retRender };
  App.createTask = createTask;

  // =================== Model ===================
  function metricCards(m) {
    function k(name, val, note) { return '<article class="card ' + (name === "Recall" ? "yellow" : "light") + ' pop"><div class="kpi-h"><span>' + name + '</span></div><div class="kpi-v mono">' + val + '</div><div class="kpi-d">' + note + "</div></article>"; }
    return '<div class="grid4">' + k("Accuracy", (m.accuracy * 100).toFixed(1) + "%", "Share of all predictions that were right") +
      k("Precision", (m.precision * 100).toFixed(1) + "%", "Of customers flagged, how many really left") +
      k("Recall", (m.recall * 100).toFixed(1) + "%", "Of customers who left, how many were caught") +
      k("F1-score", m.f1.toFixed(2), "Balance of precision and recall") + "</div>";
  }
  function rocSVG(m) {
    var W = 260, H = 240, L = 34, B = 30, T = 10, R = 10, pw = W - L - R, ph = H - T - B;
    var pts = m.roc.map(function (p) { return (L + p[0] * pw).toFixed(1) + "," + (T + ph - p[1] * ph).toFixed(1); }).join(" ");
    var grid = [0, .5, 1].map(function (v) {
      return '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + (T + ph - v * ph) + '" y2="' + (T + ph - v * ph) + '" style="stroke:var(--line)"/><text x="' + (L - 6) + '" y="' + (T + ph - v * ph + 4) + '" text-anchor="end">' + v + "</text>" +
        '<text x="' + (L + v * pw) + '" y="' + (H - 14) + '" text-anchor="middle">' + v + "</text>";
    }).join("");
    return '<svg class="chart roc" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="ROC curve, AUC ' + m.auc.toFixed(2) + '">' + grid +
      '<line x1="' + L + '" y1="' + (T + ph) + '" x2="' + (W - R) + '" y2="' + T + '" style="stroke:var(--muted)" stroke-opacity=".6" stroke-dasharray="4 4"/>' +
      '<polyline points="' + pts + '" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>' +
      '<text x="' + (W / 2) + '" y="' + (H - 1) + '" text-anchor="middle">False positive rate</text></svg>';
  }
  App.views.model = {
    render: function () {
      var I = window.MODEL_INFO || {};
      var about = '<article class="card dark pop"><h3>About the model</h3><dl class="about"><dt>Model</dt><dd>' + esc(I.name || "") + "</dd><dt>Algorithm</dt><dd>" + esc(I.algorithm || "") + "</dd><dt>Version</dt><dd>" + esc(I.version || "") + "</dd><dt>Last trained</dt><dd>" + esc(I.trained || "") + "</dd><dt>Dataset</dt><dd>" + esc(I.dataset || "") + "</dd><dt>Limitations</dt><dd>" + esc(I.limits || "") + "</dd></dl></article>";
      if (!App.list) return void body("model", about + noData("Upload a customer file to see what drives churn and how accurate the predictions are."));
      var imp = Data.importance(App.list, App.means);
      var impCard = '<article class="card light pop"><h3>What drives churn</h3><div class="sub">Share of each factor in the predictions for this dataset</div><div class="imp">' +
        imp.map(function (f) { return '<div class="imp-row"><span>' + f.name + '</span><span class="trk"><b style="width:' + Math.round(f.share * 100) + '%"></b></span><span class="mono">' + Math.round(f.share * 100) + "%</span></div>"; }).join("") + "</div></article>";
      var m = Data.metrics(App.list), met;
      if (!m) met = '<article class="card light pop c-full"><h3>Evaluation</h3><p class="sub" style="margin-top:6px">To measure accuracy, upload a file with a <b>churned</b> column (1 = left, 0 = stayed) for at least 10 customers. The bundled sample data has one.</p></article>';
      else if (m.onlyOneClass) met = '<article class="card light pop c-full"><h3>Evaluation</h3><p class="sub" style="margin-top:6px">Every customer in the churned column has the same outcome, so precision, recall and AUC can\'t be calculated.</p></article>';
      else {
        var tot = Math.max(m.actualChurn, m.predictedChurn, 1);
        met = metricCards(m) +
          '<div class="grid2" style="margin-top:12px"><article class="card light pop"><h3>Confusion matrix</h3><div class="sub">' + m.n + ' customers · churn if probability is ' + Math.round(Data.CHURN_AT * 100) + '% or more</div>' +
          '<div class="cm"><span></span><b>Predicted stay</b><b>Predicted churn</b><b>Actual stay</b><div class="ok">' + m.tn + '<small>true negatives</small></div><div class="bad">' + m.fp + '<small>false alarms</small></div><b>Actual churn</b><div class="bad">' + m.fn + '<small>missed</small></div><div class="ok">' + m.tp + '<small>caught</small></div></div></article>' +
          '<article class="card light pop"><h3>ROC curve</h3><div class="sub">AUC = <b class="mono">' + m.auc.toFixed(3) + '</b> (1.0 is perfect, 0.5 is a coin flip)</div>' + rocSVG(m) + "</article></div>" +
          '<article class="card light pop" style="margin-top:12px"><h3>Predicted vs actual churn</h3><div class="pva"><div><span>Actually churned</span><span class="trk"><b style="width:' + m.actualChurn / tot * 100 + '%;background:var(--dark)"></b></span><span class="mono">' + m.actualChurn + '</span></div>' +
          '<div><span>Predicted to churn</span><span class="trk"><b style="width:' + m.predictedChurn / tot * 100 + '%;background:var(--y2)"></b></span><span class="mono">' + m.predictedChurn + "</span></div></div>" +
          '<p class="sub" style="margin-top:10px">Check recall as well as accuracy. A model can look accurate and still miss many customers who leave.</p></article>';
      }
      body("model", '<div class="grid2">' + about + impCard + "</div><div style=\"margin-top:12px\">" + met + "</div>");
    }
  };

  // =================== Activity ===================
  function histRows() {
    var h = Store.get("history", []);
    if (!h.length) return '<p class="sub" style="margin-top:8px">No predictions yet. Upload a dataset or run a manual prediction.</p>';
    return '<div class="tbl-wrap"><table class="big"><thead><tr><th>When</th><th>Type</th><th>Customer / file</th><th>Result</th></tr></thead><tbody>' + h.slice(0, 100).map(function (x) {
      var res = x.type === "bulk" ? x.count + " predicted · " + x.high + " high risk" + (x.failed ? " · " + x.failed + " rows failed" : "") : pct(x.p) + "% " + pill(x.risk);
      return "<tr><td class=\"mono\">" + App.fmtDate(x.ts) + "</td><td>" + (x.type === "bulk" ? "Bulk upload" : "Manual") + "</td><td>" + esc(x.customer) + "</td><td>" + res + "</td></tr>";
    }).join("") + "</tbody></table></div>";
  }
  App.views.activity = {
    render: function () {
      var audit = "";
      if (App.can("audit")) {
        var a = Store.get("audit", []);
        audit = '<article class="card light pop" style="margin-top:12px"><div class="rep-head"><h3>Audit log</h3><span class="sub">Latest 100 actions</span></div>' + (a.length ? '<div class="tbl-wrap"><table class="big"><thead><tr><th>When</th><th>User</th><th>Role</th><th>Action</th><th>Details</th></tr></thead><tbody>' +
          a.slice(0, 100).map(function (x) { return '<tr><td class="mono">' + App.fmtDate(x.ts) + "</td><td>" + esc(x.user) + "</td><td>" + esc(x.role) + "</td><td>" + esc(x.action) + "</td><td>" + esc(x.detail) + "</td></tr>"; }).join("") + "</tbody></table></div>" : '<p class="sub">Nothing logged yet.</p>') + "</article>";
      } else audit = '<article class="card light pop" style="margin-top:12px"><h3>Audit log</h3><p class="sub" style="margin-top:6px">Only admins can see the audit log. Change the demo role in Settings.</p></article>';
      body("activity", '<article class="card light pop"><div class="rep-head"><h3>Prediction history</h3><div class="row"><button class="pbtn" type="button" id="expHist">⬇ Export CSV</button><button class="pbtn" type="button" id="clrHist"' + (App.can("write") ? "" : " disabled") + ">Clear history</button></div></div>" + histRows() + "</article>" + audit);
      $("expHist").addEventListener("click", function () {
        var h = Store.get("history", []);
        var csv = "timestamp,type,customer_or_file,churn_probability,risk,rows,high_risk,failed_rows\n" + h.map(function (x) {
          return [new Date(x.ts).toISOString(), x.type, '"' + String(x.customer).replace(/"/g, '""') + '"', x.p != null ? x.p.toFixed(4) : "", x.risk || "", x.count || "", x.high != null ? x.high : "", x.failed || ""].join(",");
        }).join("\n");
        App.download("prediction_history.csv", csv); Store.audit("Exported history", h.length + " entries");
      });
      $("clrHist").addEventListener("click", function () {
        var b = $("clrHist"); if (b.dataset.sure !== "1") { b.dataset.sure = "1"; b.textContent = "Click again to confirm"; return; }
        Store.del("history"); Store.audit("Cleared prediction history", ""); App.views.activity.render();
      });
    }
  };

  App.start();
})();
