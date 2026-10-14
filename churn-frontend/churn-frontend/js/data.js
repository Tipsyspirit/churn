// Data layer: CSV parsing + validation, scoring, explanations, metrics, summaries.
(function () {
  var ALIASES = {
    id:       ["customer_id", "customerid", "id", "customer"],
    tenure:   ["tenure_months", "tenure"],
    orders:   ["orders_90d", "orders", "order_count"],
    days:     ["days_since_last_order", "recency", "days_since_order"],
    tickets:  ["support_tickets", "tickets", "complaints"],
    aov:      ["avg_order_value", "aov", "avg_order"],
    discount: ["discount_use_pct", "discount_use", "discount"],
    actual:   ["churned", "churn", "actual_churn", "label", "is_churn"]
  };
  var NUM = ["tenure", "orders", "days", "tickets", "aov", "discount"];
  var DEFAULTS = { tenure: 12, orders: 3, days: 30, tickets: 0, aov: 1500, discount: 20 };
  var LABELS = { tenure: "tenure_months", orders: "orders_90d", days: "days_since_last_order", tickets: "support_tickets", aov: "avg_order_value", discount: "discount_use_pct" };
  // Probability at which a customer counts as "likely to churn". Admins can change it in Settings.
  function churnAt() { return (window.APP_PREFS && window.APP_PREFS.churnAt) || 0.5; }

  // ---------- CSV ----------
  function parseCSV(text) {
    text = String(text).replace(/^﻿/, "");
    var rows = [], row = [], cur = "", q = false;
    for (var i = 0; i < text.length; i++) {
      var c = text[i];
      if (q) {
        if (c === '"') { if (text[i + 1] === '"') { cur += '"'; i++; } else q = false; }
        else cur += c;
      } else if (c === '"') q = true;
      else if (c === ",") { row.push(cur); cur = ""; }
      else if (c === "\n" || c === "\r") {
        if (c === "\r" && text[i + 1] === "\n") i++;
        row.push(cur); cur = "";
        if (row.length > 1 || row[0] !== "") rows.push(row);
        row = [];
      } else cur += c;
    }
    if (cur !== "" || row.length) { row.push(cur); if (row.length > 1 || row[0] !== "") rows.push(row); }
    return rows;
  }

  function mapColumns(headers) {
    var idx = {}, missing = [];
    var low = headers.map(function (h) { return h.trim().toLowerCase(); });
    Object.keys(ALIASES).forEach(function (k) {
      var at = -1;
      ALIASES[k].some(function (a) { at = low.indexOf(a); return at >= 0; });
      idx[k] = at;
      if (at < 0) missing.push(k);
    });
    return { idx: idx, missing: missing };
  }

  function parseActual(v) {
    v = String(v == null ? "" : v).trim().toLowerCase();
    if (["1", "yes", "y", "true", "churned", "left"].indexOf(v) >= 0) return 1;
    if (["0", "no", "n", "false", "stayed", "retained"].indexOf(v) >= 0) return 0;
    return null;
  }
  function median(a) {
    if (!a.length) return null;
    var s = a.slice().sort(function (x, y) { return x - y; }), m = Math.floor(s.length / 2);
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
  }

  // Never silently drops rows: every skipped row is listed in report.errors.
  function toCustomers(table) {
    var head = table[0], map = mapColumns(head);
    var rep = { totalRows: table.length - 1, valid: 0, failed: 0, filled: 0, errors: [], warnings: [] };
    var missingNum = map.missing.filter(function (k) { return NUM.indexOf(k) >= 0; });
    missingNum.forEach(function (k) { rep.warnings.push('Column "' + LABELS[k] + '" was not found. Using ' + DEFAULTS[k] + " for every customer."); });
    if (map.idx.id < 0) rep.warnings.push("No customer_id column. IDs were generated (C-1, C-2, ...).");
    if (map.idx.actual < 0) rep.warnings.push('No "churned" column. Model evaluation needs actual outcomes (0 or 1).');

    var seen = {}, rows = [];
    function err(row, msg) { rep.errors.push({ row: row, msg: msg }); }
    table.slice(1).forEach(function (r, i) {
      var rowNo = i + 2;
      if (r.length !== head.length) return err(rowNo, "Expected " + head.length + " columns but found " + r.length + ".");
      var c = {}, bad = null, blanks = 0;
      NUM.forEach(function (k) {
        if (bad) return;
        if (map.idx[k] < 0) { c[k] = DEFAULTS[k]; return; }
        var raw = (r[map.idx[k]] || "").trim();
        if (raw === "") { c[k] = null; blanks++; return; }
        var n = Number(raw.replace(/,/g, ""));
        if (!isFinite(n)) { bad = LABELS[k] + ' is not a number ("' + raw + '").'; return; }
        if (n < 0 || (k === "discount" && n > 100)) { bad = LABELS[k] + " is out of range (" + raw + ")."; return; }
        c[k] = n;
      });
      if (bad) return err(rowNo, bad);
      var id = map.idx.id >= 0 ? (r[map.idx.id] || "").trim() : "";
      if (!id) id = "C-" + (i + 1);
      if (seen[id]) return err(rowNo, 'Duplicate customer ID "' + id + '".');
      seen[id] = 1;
      c.id = id; c._blanks = blanks;
      c.actual = map.idx.actual >= 0 ? parseActual(r[map.idx.actual]) : null;
      rows.push(c);
    });
    NUM.forEach(function (k) {
      var m = median(rows.map(function (c) { return c[k]; }).filter(function (v) { return v != null; }));
      rows.forEach(function (c) { if (c[k] == null) { c[k] = m != null ? m : DEFAULTS[k]; rep.filled++; } });
    });
    rows.forEach(function (c) { delete c._blanks; });
    if (rep.filled) rep.warnings.push(rep.filled + " blank value" + (rep.filled > 1 ? "s were" : " was") + " filled with the column median.");
    rep.valid = rows.length; rep.failed = rep.totalRows - rows.length;
    return { customers: rows, missing: map.missing, missingNum: missingNum, report: rep };
  }

  // ---------- Scoring ----------
  var COEF = { days: 0.034, tickets: 0.42, tenure: -0.025, orders: -0.12, discount: 0.012 };
  var BIAS = -3.2;
  // DEMO scoring so the app works before the real model exists. See PREDICT_URL in config.js.
  function demoScore(c) {
    var z = BIAS + COEF.days * c.days + COEF.tickets * c.tickets + COEF.tenure * c.tenure + COEF.orders * c.orders + COEF.discount * c.discount;
    return 1 / (1 + Math.exp(-z));
  }

  function predict(customers) {
    if (window.PREDICT_URL) {
      return fetch(window.PREDICT_URL, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(customers) })
        .then(function (r) { if (!r.ok) throw new Error("Prediction server returned " + r.status); return r.json(); })
        .then(function (out) {
          var byId = {}; out.forEach(function (o) { byId[o.id] = o.churn_probability; });
          return customers.map(function (c) {
            if (byId[c.id] == null) throw new Error("Prediction server returned no result for " + c.id);
            return Object.assign({}, c, { p: byId[c.id] });
          });
        });
    }
    return Promise.resolve(customers.map(function (c) { return Object.assign({}, c, { p: demoScore(c) }); }));
  }

  function riskOf(p) {
    var R = window.RISK || { lowBelow: 0.4, highAbove: 0.7 };
    return p < R.lowBelow ? "low" : (p > R.highAbove ? "high" : "med");
  }

  var ACTIONS = { high: "Call + 15% win-back offer", med: "Send reminder email + reward", low: "Keep in regular newsletter" };
  var NEXT = {
    high: "Contact the customer within 3 days to understand their concerns, then offer a win-back incentive.",
    med: "Send a reminder email with a small loyalty reward and check again in two weeks.",
    low: "No action needed. Keep the customer in regular communications."
  };

  // ---------- Explanations (reasons) ----------
  var DEFAULT_MEANS = { days: 30, tickets: 1, tenure: 20, orders: 5, discount: 25 };
  function means(list) {
    var m = {}; Object.keys(COEF).forEach(function (k) { m[k] = list.length ? list.reduce(function (s, c) { return s + c[k]; }, 0) / list.length : DEFAULT_MEANS[k]; });
    return m;
  }
  var TEXT = {
    days:     function (c) { return "Long gap since the last order (" + Math.round(c.days) + " days)"; },
    tickets:  function (c) { return "Frequent support tickets (" + Math.round(c.tickets) + ")"; },
    tenure:   function (c) { return "Short time as a customer (" + Math.round(c.tenure) + " months)"; },
    orders:   function (c) { return "Few orders in the last 90 days (" + Math.round(c.orders) + ")"; },
    discount: function (c) { return "Heavy use of discounts (" + Math.round(c.discount) + "%)"; }
  };
  var GOOD = {
    days:     function (c) { return "Ordered recently (" + Math.round(c.days) + " days ago)"; },
    tickets:  function (c) { return "Few support tickets (" + Math.round(c.tickets) + ")"; },
    tenure:   function (c) { return "Long-standing customer (" + Math.round(c.tenure) + " months)"; },
    orders:   function (c) { return "Orders often (" + Math.round(c.orders) + " in 90 days)"; },
    discount: function (c) { return "Buys at full price mostly (" + Math.round(c.discount) + "% discount use)"; }
  };
  // Contribution of each feature to this customer's score, relative to the average customer.
  function explain(c, m) {
    m = m || DEFAULT_MEANS;
    var items = Object.keys(COEF).map(function (k) { return { key: k, v: COEF[k] * (c[k] - m[k]) }; });
    var maxAbs = Math.max.apply(null, items.map(function (i) { return Math.abs(i.v); }).concat([0.0001]));
    var up = items.filter(function (i) { return i.v > 0.15; }).sort(function (a, b) { return b.v - a.v; })
      .map(function (i) { return { key: i.key, text: TEXT[i.key](c), share: i.v / maxAbs }; });
    var down = items.filter(function (i) { return i.v < -0.15; }).sort(function (a, b) { return a.v - b.v; })
      .map(function (i) { return { key: i.key, text: GOOD[i.key](c), share: -i.v / maxAbs }; });
    return { up: up, down: down };
  }
  var FNAMES = { days: "Days since last order", tickets: "Support tickets", tenure: "Tenure", orders: "Orders (90 days)", discount: "Discount use" };
  function importance(list, m) {
    var tot = 0, out = Object.keys(COEF).map(function (k) {
      var v = list.reduce(function (s, c) { return s + Math.abs(COEF[k] * (c[k] - m[k])); }, 0) / (list.length || 1);
      tot += v; return { key: k, name: FNAMES[k], v: v };
    });
    out.forEach(function (o) { o.share = tot ? o.v / tot : 0; });
    return out.sort(function (a, b) { return b.share - a.share; });
  }

  // ---------- Metrics (need actual outcomes) ----------
  function metrics(list) {
    var rows = list.filter(function (c) { return c.actual === 0 || c.actual === 1; });
    if (rows.length < 10) return null;
    var tp = 0, fp = 0, fn = 0, tn = 0;
    rows.forEach(function (c) {
      var pred = c.p >= churnAt() ? 1 : 0;
      if (pred && c.actual) tp++; else if (pred && !c.actual) fp++; else if (!pred && c.actual) fn++; else tn++;
    });
    var P = tp + fn, N = tn + fp;
    if (!P || !N) return { onlyOneClass: true, n: rows.length };
    var prec = tp + fp ? tp / (tp + fp) : 0, rec = tp / P;
    // ROC curve + AUC
    var sorted = rows.slice().sort(function (a, b) { return b.p - a.p; }), pts = [[0, 0]], ctp = 0, cfp = 0, auc = 0;
    sorted.forEach(function (c, i) {
      if (c.actual) ctp++; else cfp++;
      var next = sorted[i + 1];
      if (!next || next.p !== c.p) {
        var prev = pts[pts.length - 1], x = cfp / N, y = ctp / P;
        auc += (x - prev[0]) * (y + prev[1]) / 2; pts.push([x, y]);
      }
    });
    return { n: rows.length, tp: tp, fp: fp, fn: fn, tn: tn, accuracy: (tp + tn) / rows.length, precision: prec, recall: rec,
             f1: prec + rec ? 2 * prec * rec / (prec + rec) : 0, auc: auc, roc: pts, actualChurn: P, predictedChurn: tp + fp };
  }

  // ---------- Summaries ----------
  function bucketBy(list, key, edges) {
    return edges.slice(0, -1).map(function (lo, i) {
      var hi = edges[i + 1];
      var inb = list.filter(function (c) { return c[key] >= lo && c[key] < hi; });
      return { lo: lo, hi: hi, n: inb.length, high: inb.filter(function (c) { return riskOf(c.p) === "high"; }).length,
               avg: inb.length ? inb.reduce(function (s, c) { return s + c.p; }, 0) / inb.length : 0 };
    });
  }
  function summarize(list) {
    var n = list.length, counts = { low: 0, med: 0, high: 0 }, revenue = { low: 0, med: 0, high: 0 };
    list.forEach(function (c) { var r = riskOf(c.p); counts[r]++; revenue[r] += c.aov * c.orders / 3; });
    return {
      total: n, counts: counts, revenue: revenue,
      churnRate: n ? list.filter(function (c) { return c.p >= churnAt(); }).length / n * 100 : 0,
      avgRisk: n ? list.reduce(function (s, c) { return s + c.p; }, 0) / n * 100 : 0,
      byTenure: bucketBy(list, "tenure", [0, 4, 7, 13, 25, 49, 1e9]),
      byRecency: bucketBy(list, "days", [0, 15, 30, 45, 60, 75, 90, 1e9]),
      top: list.slice().sort(function (a, b) { return b.p - a.p; }).slice(0, 7)
    };
  }

  // ---------- Revenue statement (estimated) ----------
  // Monthly revenue per customer is estimated as avg order value x orders in 90 days / 3.
  function monthlyRevenue(c) { return c.aov * c.orders / 3; }
  function revBuckets(list, key, edges, onlyHigh) {
    return edges.slice(0, -1).map(function (lo, i) {
      var hi = edges[i + 1], rev = 0, n = 0;
      list.forEach(function (c) {
        if (c[key] >= lo && c[key] < hi && (!onlyHigh || riskOf(c.p) === "high")) { rev += monthlyRevenue(c); n++; }
      });
      return { lo: lo, hi: hi, rev: rev, n: n };
    });
  }
  function statement(list) {
    var tier = { low: 0, med: 0, high: 0 }, cnt = { low: 0, med: 0, high: 0 }, total = 0;
    list.forEach(function (c) { var r = riskOf(c.p), v = monthlyRevenue(c); tier[r] += v; cnt[r]++; total += v; });
    var m = metrics(list);
    return { total: total, tier: tier, cnt: cnt, n: list.length,
      byTenure: revBuckets(list, "tenure", [0, 4, 7, 13, 25, 49, 1e9], false),
      highByRecency: revBuckets(list, "days", [0, 15, 30, 45, 60, 75, 90, 1e9], true),
      metrics: m && !m.onlyOneClass ? m : null };
  }
  function toCSV(list) {
    var body = list.map(function (c) { return [c.id, c.p.toFixed(4), riskOf(c.p), '"' + ACTIONS[riskOf(c.p)] + '"'].join(","); });
    return "customer_id,churn_probability,risk,suggested_action\n" + body.join("\n");
  }

  window.Data = { parseCSV: parseCSV, toCustomers: toCustomers, predict: predict, riskOf: riskOf, summarize: summarize, toCSV: toCSV,
    ACTIONS: ACTIONS, NEXT: NEXT, explain: explain, means: means, importance: importance, metrics: metrics,
    DEFAULT_MEANS: DEFAULT_MEANS, DEFAULTS: DEFAULTS, LABELS: LABELS, statement: statement,
    get CHURN_AT() { return churnAt(); } };
})();
