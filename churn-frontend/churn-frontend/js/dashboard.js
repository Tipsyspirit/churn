// Dashboard shell: login guard, page switching, upload + validation, loading animation, Home page.
(function () {
  var user = Auth.requireAuth();
  if (!user) return;

  var $ = function (id) { return document.getElementById(id); };
  var NS = "http://www.w3.org/2000/svg";
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var VIEWS = ["home", "customers", "predict", "retention", "report", "model", "activity", "settings"];

  var saved = Store.get("settings", null);
  if (saved && saved.low && saved.high) window.RISK = { lowBelow: saved.low, highAbove: saved.high };

  // User preferences (see Settings). Only settings that actually change behaviour are listed.
  var PREF_DEFAULTS = { explain: true, churnAt: 0.5, notifyHigh: true, notifyFail: true, autoTasks: false, dueHigh: 3, dueMed: 7, density: "comfortable" };
  window.APP_PREFS = Object.assign({}, PREF_DEFAULTS, Store.get("prefs", {}));
  function applyPrefs() { document.body.classList.toggle("compact", window.APP_PREFS.density === "compact"); }
  applyPrefs();

  var App = window.App = {
    user: user, list: null, summary: null, report: null, fileName: "", means: Data.DEFAULT_MEANS, views: {},
    $: $, reduce: reduce, can: Auth.can, VIEWS: VIEWS
  };

  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  App.esc = esc;
  App.fmtDate = function (ts) { return new Date(ts).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" }); };
  App.inr = function (v) { return "₹" + Math.round(v).toLocaleString("en-IN"); };
  App.download = function (name, text) {
    var a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([text], { type: "text/csv" })); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
  };
  var toastT;
  App.toast = function (m) { var t = $("toast"); t.textContent = m; t.classList.add("on"); clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove("on"); }, 2400); };
  App.setPref = function (k, v, quiet) {
    window.APP_PREFS[k] = v; Store.set("prefs", window.APP_PREFS); applyPrefs();
    if (!quiet) Store.audit("Changed setting", k + " → " + v);
  };
  App.prefDefaults = PREF_DEFAULTS;
  App.popIn = function (root) {
    root.querySelectorAll(".pop").forEach(function (el, i) { el.classList.remove("in"); el.style.setProperty("--i", i); void el.offsetWidth; el.classList.add("in"); });
  };

  // ---------- header / account ----------
  var first = (user.name || "there").split(" ")[0];
  $("greet").textContent = "Hi, " + first;
  var av = $("avatarBtn");
  if (user.picture) { var im = document.createElement("img"); im.src = user.picture; im.alt = ""; im.referrerPolicy = "no-referrer"; av.appendChild(im); }
  else av.textContent = (user.name || "U").split(" ").map(function (w) { return w[0]; }).slice(0, 2).join("").toUpperCase();
  App.refreshRole = function () {
    var u = Auth.getUser() || user; App.user = u;
    $("roleChip").textContent = u.role;
    $("who").innerHTML = "<b>" + esc(u.name || "Signed in") + "</b>" + esc(u.email || "") + " · " + esc(u.role);
  };
  App.refreshRole();
  av.addEventListener("click", function () { var open = $("menuPop").hidden; $("menuPop").hidden = !open; av.setAttribute("aria-expanded", String(open)); });
  document.addEventListener("click", function (e) { if (!e.target.closest(".menu")) { $("menuPop").hidden = true; av.setAttribute("aria-expanded", "false"); } });
  function closeMenu(focusBtn) { $("menuPop").hidden = true; av.setAttribute("aria-expanded", "false"); if (focusBtn) av.focus(); }
  // Every settings section lives in the profile menu
  $("menuPop").addEventListener("click", function (e) {
    var item = e.target.closest("[data-set]"); if (!item) return;
    closeMenu(false); App.openSettings(item.dataset.set);
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !$("menuPop").hidden) closeMenu(true); });
  window.addEventListener("themechange", function () { Store.audit("Changed theme", Theme.get()); App.toast(Theme.get() === "dark" ? "Dark mode on" : "Light mode on"); });
  $("signOut").addEventListener("click", Auth.signOut);
  $("newUpload").addEventListener("click", function () { $("menuPop").hidden = true; openUpload(); });
  $("reupload").addEventListener("click", openUpload);
  $("exportBtn").addEventListener("click", function () {
    App.download("churn_predictions.csv", Data.toCSV(App.list));
    Store.audit("Exported predictions", App.list.length + " rows");
  });
  document.addEventListener("click", function (e) {
    var g = e.target.closest("[data-go]"); if (g) App.show(g.dataset.go);
    var a = e.target.closest('[data-act="goUpload"]'); if (a) openUpload();
  });

  // ---------- page switching ----------
  App.show = function (v) {
    if (VIEWS.indexOf(v) < 0) v = "home";
    VIEWS.forEach(function (n) { $("view-" + n).hidden = n !== v; });
    document.querySelectorAll("#tabs button").forEach(function (b) { if (b.dataset.view === v) b.setAttribute("aria-current", "page"); else b.removeAttribute("aria-current"); });
    if (location.hash !== "#" + v) history.replaceState(null, "", "#" + v);
    if (v === "home") { if (App.list) App.popIn($("board")); }
    else if (App.views[v]) App.views[v].render();
    window.scrollTo({ top: 0 });
  };
  $("tabs").addEventListener("click", function (e) { var b = e.target.closest("button"); if (b) App.show(b.dataset.view); });
  window.addEventListener("hashchange", function () { var v = location.hash.slice(1); if (VIEWS.indexOf(v) >= 0 && $("view-" + v).hidden) App.show(v); });

  // ---------- upload ----------
  var drop = $("drop");
  ["dragenter", "dragover"].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add("over"); }); });
  ["dragleave", "drop"].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove("over"); }); });
  drop.addEventListener("drop", function (e) { var f = e.dataTransfer.files[0]; if (f) readFile(f); });
  $("file").addEventListener("change", function (e) { var f = e.target.files[0]; if (f) readFile(f); e.target.value = ""; });
  $("useSample").addEventListener("click", function () { if (needWrite()) return; analyze(window.SAMPLE_CSV, "sample_customers.csv"); });
  $("dlSample").addEventListener("click", function () { App.download("sample_customers.csv", window.SAMPLE_CSV); });
  $("cancelUpload").addEventListener("click", function () { $("uploadView").hidden = true; $("board").hidden = false; $("actions").hidden = false; });
  function showErr(m) { $("err").textContent = m; }
  function needWrite() { if (Auth.can("write")) return false; showErr("Your role is read-only (viewer). Change the demo role in Settings to upload data."); return true; }
  function readFile(f) {
    if (needWrite()) return;
    if (!/\.csv$/i.test(f.name)) return showErr("Please choose a .csv file.");
    var r = new FileReader();
    r.onload = function () { analyze(String(r.result), f.name); };
    r.onerror = function () { showErr("Couldn't read that file. Try again."); };
    r.readAsText(f);
  }
  function openUpload() {
    App.show("home");
    $("board").hidden = true; $("actions").hidden = true; $("uploadView").hidden = false;
    $("cancelUpload").hidden = !App.list; showErr("");
    $("subtitle").textContent = "Upload a customer file to see churn predictions.";
  }

  // ---------- loading sequence ----------
  function wait(ms) { return new Promise(function (r) { setTimeout(r, reduce ? 0 : ms); }); }
  function setStep(i) {
    var lis = $("lsteps").children;
    for (var k = 0; k < lis.length; k++) lis[k].className = k < i ? "done" : (k === i ? "now" : "");
    $("lbar").style.width = Math.min(100, (i / lis.length) * 100 + 8) + "%";
  }
  function analyze(text, name) {
    showErr("");
    var table = Data.parseCSV(text);
    if (table.length < 2) return showErr("That file has no data rows.");
    var parsed = Data.toCustomers(table);
    if (!parsed.customers.length) {
      var e0 = parsed.report.errors[0];
      return showErr("No valid rows found." + (e0 ? " First problem: row " + e0.row + ". " + e0.msg : ""));
    }
    if (parsed.missingNum.length >= 6) return showErr("None of the expected columns were found. Check the header row.");

    $("uploadView").hidden = true; $("loader").hidden = false; setStep(0);
    var result;
    wait(650).then(function () { setStep(1); return wait(700); })
      .then(function () { setStep(2); return Promise.all([Data.predict(parsed.customers), wait(900)]); })
      .then(function (out) { result = out[0]; setStep(3); return wait(700); })
      .then(function () {
        load({ name: name, customers: result, report: parsed.report, missingNum: parsed.missingNum });
        Store.set("dataset", { name: name, customers: result, report: parsed.report, missingNum: parsed.missingNum, ts: Date.now() });
        Store.addHistory({ type: "bulk", customer: name, count: result.length, high: App.summary.counts.high, failed: parsed.report.failed });
        Store.audit("Uploaded dataset", name + " · " + result.length + " valid, " + parsed.report.failed + " failed");
        $("lbar").style.width = "100%";
        return wait(250);
      })
      .then(function () { $("loader").hidden = true; reveal(); afterUpload(parsed.report); })
      .catch(function (e) {
        $("loader").hidden = true; $("uploadView").hidden = false;
        showErr("Something went wrong: " + (e && e.message ? e.message : "unknown error"));
      });
  }

  // In-app alerts and automatic follow-up tasks, controlled by Settings
  function afterUpload(rep) {
    var P = window.APP_PREFS, msgs = [], high = App.list.filter(function (c) { return Data.riskOf(c.p) === "high"; });
    if (P.autoTasks && Auth.can("write") && App.createTask) {
      var n = 0; high.forEach(function (c) { if (App.createTask(c, true)) n++; });
      if (n) { Store.audit("Auto-created retention tasks", n + " high-risk customers"); msgs.push(n + " follow-up tasks created"); }
    }
    if (P.notifyHigh && high.length) msgs.unshift(high.length + " high-risk customer" + (high.length > 1 ? "s" : "") + " found");
    if (P.notifyFail && rep.failed) msgs.push(rep.failed + " row" + (rep.failed > 1 ? "s" : "") + " failed validation");
    if (msgs.length) setTimeout(function () { App.toast(msgs.join(" · ")); }, reduce ? 0 : 1200);
  }

  function load(d) {
    App.list = d.customers; App.fileName = d.name; App.report = d.report;
    App.means = Data.means(d.customers);
    App.summary = Data.summarize(d.customers);
    render(App.summary, d.missingNum || [], d.report);
  }
  // Re-render after risk thresholds change
  App.recompute = function () { if (!App.list) return; App.summary = Data.summarize(App.list); render(App.summary, [], App.report); App.popIn($("board")); };

  function reveal() {
    $("board").hidden = false; $("actions").hidden = false; $("cancelUpload").hidden = false;
    $("subtitle").textContent = "Showing " + App.summary.total.toLocaleString("en-IN") + " customers from " + App.fileName;
    App.show("home");
    App.popIn($("board"));
    document.querySelectorAll("#board [data-count]").forEach(countUp);
  }

  // ---------- count-up numbers ----------
  function fmt(el, v) {
    var t = el.dataset.type;
    el.textContent = t === "pct" ? v.toFixed(1) + "%" : t === "inr" ? "₹" + Math.round(v).toLocaleString("en-IN") : Math.round(v).toLocaleString("en-IN");
  }
  function countUp(el) {
    var end = +el.dataset.count;
    if (reduce) return fmt(el, end);
    var pop = el.closest(".pop"), t0 = performance.now() + (pop ? (+pop.style.getPropertyValue("--i") || 0) * 85 : 0), dur = 1100;
    fmt(el, 0);
    (function step(t) { var k = Math.max(0, Math.min(1, (t - t0) / dur)), e = 1 - Math.pow(1 - k, 3); fmt(el, end * e); if (k < 1) requestAnimationFrame(step); })(performance.now());
  }
  function setCount(id, val, type) { var el = $(id); el.dataset.count = val; el.dataset.type = type; fmt(el, val); }

  // ---------- Home rendering ----------
  function el(tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (parent) parent.appendChild(n); return n;
  }
  function label(lo, hi) { return hi > 1e8 ? lo + "+" : lo + "–" + (hi - 1); }
  var tip = $("tip");
  function showTip(e, html) { tip.innerHTML = html; tip.classList.add("on"); tip.style.left = Math.min(innerWidth - 190, e.clientX + 14) + "px"; tip.style.top = (e.clientY + 14) + "px"; }
  function hideTip() { tip.classList.remove("on"); }

  function render(s, missingNum, report) {
    $("subtitle").textContent = "Showing " + s.total.toLocaleString("en-IN") + " customers from " + App.fileName;
    setCount("k-total", s.total, "int");
    $("k-total-d").textContent = missingNum.length ? "Defaults used for " + missingNum.length + " missing column" + (missingNum.length > 1 ? "s" : "") : "All expected columns found";
    setCount("k-rate", s.churnRate, "pct");
    $("k-rate-d").textContent = "Customers with " + Math.round(Data.CHURN_AT * 100) + "%+ churn probability";
    setCount("k-high", s.counts.high, "int");
    $("k-high-d").textContent = (s.total ? (s.counts.high / s.total * 100).toFixed(1) : 0) + "% of all customers";
    setCount("k-rev", s.revenue.high, "inr");
    setCount("k-avg", s.avgRisk, "pct");
    reportCard(report);
    bars(s.byTenure); sparkline(s.byRecency); line(s.byRecency);
    actions(s); table(s.top); donut(s); segments(s);
  }

  function reportCard(r) {
    var ok = r.failed === 0;
    var errs = r.errors.slice(0, 8).map(function (e) { return "<li><b>Row " + e.row + "</b> " + esc(e.msg) + "</li>"; }).join("");
    var more = r.errors.length > 8 ? '<li class="sub">…and ' + (r.errors.length - 8) + " more.</li>" : "";
    var warns = r.warnings.map(function (w) { return "<li>" + esc(w) + "</li>"; }).join("");
    $("reportCard").innerHTML =
      '<div class="rep-head"><h3>Upload report</h3><span class="pill ' + (ok ? "low" : "med") + '">' + (ok ? "All rows used" : r.failed + " row" + (r.failed > 1 ? "s" : "") + " skipped") + "</span></div>" +
      '<div class="rep-nums"><div><b class="mono">' + r.totalRows.toLocaleString("en-IN") + '</b><span>rows in file</span></div><div><b class="mono" style="color:var(--low)">' + r.valid.toLocaleString("en-IN") +
      '</b><span>predicted</span></div><div><b class="mono" style="color:' + (ok ? "inherit" : "var(--high)") + '">' + r.failed.toLocaleString("en-IN") + '</b><span>failed</span></div></div>' +
      (errs ? '<details open><summary>Rows that failed validation</summary><ul class="replist">' + errs + more + "</ul></details>" : "") +
      (warns ? '<details><summary>Notes about the file</summary><ul class="replist">' + warns + "</ul></details>" : "");
  }

  function bars(b) {
    var svg = $("barChart"); svg.innerHTML = "";
    var W = 640, H = 230, L = 34, B = 26, T = 8, ph = H - B - T, pw = W - L;
    var max = Math.max.apply(null, b.map(function (x) { return x.n; })) || 1;
    var step = Math.ceil(max / 3 / 5) * 5 || 1, top = step * 3; if (top < max) top = Math.ceil(max / step) * step;
    for (var v = 0; v <= top; v += step) {
      var y = T + ph - v / top * ph;
      el("line", { x1: L, x2: W, y1: y, y2: y, stroke: "#3a3a3a", "stroke-dasharray": v ? "3 4" : "0" }, svg);
      var t = el("text", { x: L - 8, y: y + 4, "text-anchor": "end" }, svg); t.textContent = v;
    }
    var gw = pw / b.length, bw = Math.min(26, gw / 3);
    b.forEach(function (g, i) {
      var cx = L + gw * i + gw / 2;
      [[g.n, "#e9e9e4", -bw - 2, "All customers"], [g.high, "#f6ef5c", 2, "High risk"]].forEach(function (d, k) {
        var h = d[0] / top * ph, r = el("rect", { x: cx + d[2], y: T + ph - h, width: bw, height: Math.max(h, d[0] ? 2 : 0), rx: 6, fill: d[1], "class": "bar pop-bar bar-hit" }, svg);
        r.style.animationDelay = (0.5 + i * 0.07 + k * 0.05) + "s";
        r.addEventListener("mousemove", function (e) { showTip(e, "<b>" + label(g.lo, g.hi) + " months</b><br>" + d[3] + ": " + d[0]); });
        r.addEventListener("mouseleave", hideTip);
      });
      var tx = el("text", { x: cx, y: H - 6, "text-anchor": "middle" }, svg); tx.textContent = label(g.lo, g.hi);
    });
  }
  function smooth(pts) {
    var d = "M" + pts[0][0] + " " + pts[0][1];
    for (var i = 0; i < pts.length - 1; i++) {
      var p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
      d += " C" + (p1[0] + (p2[0] - p0[0]) / 6) + " " + (p1[1] + (p2[1] - p0[1]) / 6) + "," + (p2[0] - (p3[0] - p1[0]) / 6) + " " + (p2[1] - (p3[1] - p1[1]) / 6) + "," + p2[0] + " " + p2[1];
    }
    return d;
  }
  function sparkline(b) {
    var svg = $("spark"); svg.innerHTML = "";
    var pts = b.map(function (x, i) { return [i / (b.length - 1) * 296 + 2, 62 - x.avg * 54]; }), d = smooth(pts);
    el("path", { d: d + " L298 70 L2 70 Z", fill: "#16161618" }, svg);
    el("path", { d: d, fill: "none", stroke: "#161616", "stroke-width": 2.5, "stroke-linecap": "round", "class": "draw", style: "--len:600" }, svg);
    var l = pts[pts.length - 1]; el("circle", { cx: l[0], cy: l[1], r: 4.5, fill: "#161616" }, svg);
  }
  function line(b) {
    var svg = $("lineChart"); svg.innerHTML = "";
    var W = 640, H = 220, L = 38, B = 28, T = 12, ph = H - B - T, pw = W - L - 10;
    [0, 25, 50, 75, 100].forEach(function (v) {
      var y = T + ph - v / 100 * ph;
      el("line", { x1: L, x2: W - 6, y1: y, y2: y, stroke: "#c9bf3a", "stroke-dasharray": v ? "3 4" : "0" }, svg);
      var t = el("text", { x: L - 8, y: y + 4, "text-anchor": "end" }, svg); t.textContent = v + "%";
    });
    var pts = b.map(function (x, i) { return [L + 10 + i / (b.length - 1) * (pw - 20), T + ph - x.avg * ph]; }), d = smooth(pts);
    el("path", { d: d + " L" + pts[pts.length - 1][0] + " " + (T + ph) + " L" + pts[0][0] + " " + (T + ph) + " Z", fill: "#16161614" }, svg);
    el("path", { d: d, fill: "none", stroke: "#161616", "stroke-width": 3, "stroke-linecap": "round", "class": "draw", style: "--len:900" }, svg);
    pts.forEach(function (p, i) {
      var x = b[i];
      var tx = el("text", { x: p[0], y: H - 8, "text-anchor": "middle" }, svg); tx.textContent = label(x.lo, x.hi);
      var c = el("circle", { cx: p[0], cy: p[1], r: 5, fill: "#f6ef5c", stroke: "#161616", "stroke-width": 2.5, style: "cursor:pointer" }, svg);
      var hit = el("circle", { cx: p[0], cy: p[1], r: 18, fill: "transparent", style: "cursor:pointer" }, svg);
      hit.addEventListener("mousemove", function (e) { c.setAttribute("r", 7.5); showTip(e, "<b>" + label(x.lo, x.hi) + " days</b><br>Avg risk " + (x.avg * 100).toFixed(0) + "% · " + x.n + " customers"); });
      hit.addEventListener("mouseleave", function () { c.setAttribute("r", 5); hideTip(); });
    });
  }
  function actions(s) {
    var rows = [["high", "High risk", s.counts.high], ["med", "Medium risk", s.counts.med], ["low", "Low risk", s.counts.low]];
    $("actionList").innerHTML = rows.map(function (r) {
      return '<div style="display:flex;align-items:center;gap:10px;justify-content:space-between;flex-wrap:wrap"><div style="min-width:0"><span class="pill ' + r[0] + '">' + r[1] + '</span><div class="sub" style="margin-top:4px">' + Data.ACTIONS[r[0]] + '</div></div><b class="mono" style="font-size:20px">' + r[2].toLocaleString("en-IN") + "</b></div>";
    }).join("");
  }
  var STAT = { high: "High", med: "Medium", low: "Low" };
  function table(list) {
    $("rows").innerHTML = list.map(function (c, i) {
      var r = Data.riskOf(c.p), pct = Math.round(c.p * 100);
      return '<tr data-i="' + i + '" tabindex="0"><td><div class="who"><span class="av">' + esc(String(c.id).replace(/[^A-Za-z0-9]/g, "").slice(-2).toUpperCase()) + "</span>" + esc(c.id) + "</div></td>" +
        "<td>" + Data.ACTIONS[r] + '</td><td class="mono">' + Math.round(c.days) + " days ago</td>" +
        '<td class="mono"><span class="meter"><b class="' + r + '" style="width:' + pct + '%"></b></span>' + pct + "%</td>" +
        '<td><span class="pill ' + r + '">' + STAT[r] + '</span></td><td><button class="eye" type="button" aria-label="View ' + esc(c.id) + '">👁</button></td></tr>';
    }).join("");
  }
  $("rows").addEventListener("click", function (e) { var tr = e.target.closest("tr"); if (tr && App.openDrawer) App.openDrawer(App.summary.top[+tr.dataset.i]); });
  $("rows").addEventListener("keydown", function (e) { if (e.key === "Enter") { var tr = e.target.closest("tr"); if (tr && App.openDrawer) App.openDrawer(App.summary.top[+tr.dataset.i]); } });

  function donut(s) {
    var svg = $("donut"); svg.innerHTML = "";
    var R = 90, cx = 110, cy = 110, len = Math.PI * R;
    var d = "M" + (cx - R) + " " + cy + " A" + R + " " + R + " 0 0 1 " + (cx + R) + " " + cy;
    el("path", { d: d, fill: "none", style: "stroke:var(--track)", "stroke-width": 22 }, svg);
    var tot = s.revenue.high + s.revenue.med + s.revenue.low || 1, off = 0;
    [["high", "#c8352b"], ["med", "#f0a63a"], ["low", "#2f9e62"]].forEach(function (x) {
      var seg = s.revenue[x[0]] / tot * len; if (seg < 0.5) return;
      var p = el("path", { d: d, fill: "none", stroke: x[1], "stroke-width": 22, "stroke-dasharray": Math.max(seg - 2, 0.1) + " " + len, "stroke-dashoffset": -off, style: "cursor:pointer;transition:stroke-width .2s" }, svg);
      p.addEventListener("mouseenter", function () { p.setAttribute("stroke-width", 27); });
      p.addEventListener("mousemove", function (e) { showTip(e, "<b>" + STAT[x[0]] + " risk</b><br>" + App.inr(s.revenue[x[0]]) + " / month"); });
      p.addEventListener("mouseleave", function () { p.setAttribute("stroke-width", 22); hideTip(); });
      off += seg;
    });
    var dv = $("d-val"); dv.dataset.count = s.revenue.high + s.revenue.med; dv.dataset.type = "inr"; fmt(dv, +dv.dataset.count);
    var top = s.top[0];
    $("tipTitle").textContent = top ? "Start with " + top.id : "No customers";
    $("tipText").textContent = top ? Math.round(top.p * 100) + "% churn risk · " + Data.ACTIONS[Data.riskOf(top.p)] : "";
  }
  function segments(s) {
    var rows = [["low", "Low", "#2f9e62"], ["med", "Medium", "#f0a63a"], ["high", "High", "#c8352b"]];
    $("seg").innerHTML = rows.map(function (r) {
      var pct = s.total ? s.counts[r[0]] / s.total * 100 : 0;
      return '<div class="seg-row"><span>' + r[1] + '</span><span class="trk"><b data-w="' + pct + '" style="background:' + r[2] + '"></b></span><span class="pctv mono">' + Math.round(pct) + "%</span></div>";
    }).join("");
    requestAnimationFrame(function () { setTimeout(function () { document.querySelectorAll("#seg b").forEach(function (b) { b.style.width = b.dataset.w + "%"; }); }, reduce ? 0 : 700); });
  }

  // ---------- start (called by views.js once every page module is registered) ----------
  App.start = function () {
    var ds = Store.get("dataset", null);
    if (ds && ds.customers && ds.customers.length) {
      load(ds);
      $("uploadView").hidden = true; $("board").hidden = false; $("actions").hidden = false; $("cancelUpload").hidden = false;
    }
    var v = location.hash.slice(1);
    App.show(VIEWS.indexOf(v) >= 0 ? v : "home");
    if (App.list && !$("view-home").hidden) document.querySelectorAll("#board [data-count]").forEach(countUp);
  };
})();
