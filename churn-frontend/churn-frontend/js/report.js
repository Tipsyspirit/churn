// Revenue Statement Report: an income-statement style page built from the uploaded customers.
// Monthly revenue per customer is ESTIMATED as avg order value x orders in 90 days / 3. It is not an accounting income statement.
(function () {
  if (!window.App) return;
  var App = window.App, $ = App.$, esc = App.esc, inr = App.inr;
  var NS = "http://www.w3.org/2000/svg";

  function label(lo, hi) { return hi > 1e8 ? lo + "+" : lo + "–" + (hi - 1); }
  function pc(a, b) { return b ? Math.round(a / b * 100) : 0; }

  function treeRows(rows, total, unit) {
    var max = Math.max.apply(null, rows.map(function (r) { return r.rev; }).concat([1]));
    return rows.map(function (r) {
      return '<div class="t-row"><span class="t-dash" aria-hidden="true">–</span><span class="t-lab">' + label(r.lo, r.hi) + " " + unit + '<small>' + r.n + ' customers</small></span>' +
        '<span class="t-trk"><b style="width:' + Math.round(r.rev / max * 100) + '%"></b></span><span class="t-amt mono">' + inr(r.rev) + "</span></div>";
    }).join("");
  }

  function miniBars(rows) {
    var W = 260, H = 110, max = Math.max.apply(null, rows.map(function (r) { return r.rev; }).concat([1])), bw = W / rows.length;
    return '<svg class="chart" viewBox="0 0 ' + W + " " + (H + 18) + '" role="img" aria-label="Revenue by group">' + rows.map(function (r, i) {
      var h = Math.max(2, r.rev / max * H);
      return '<rect class="bar pop-bar" style="animation-delay:' + (0.4 + i * 0.06) + 's" x="' + (i * bw + bw * 0.18) + '" y="' + (H - h) + '" width="' + bw * 0.64 + '" height="' + h + '" rx="6" fill="currentColor"><title>' + label(r.lo, r.hi) + ": " + inr(r.rev) + "</title></rect>" +
        '<text x="' + (i * bw + bw / 2) + '" y="' + (H + 14) + '" text-anchor="middle">' + label(r.lo, r.hi) + "</text>";
    }).join("") + "</svg>";
  }
  function miniLine(rows) {
    var W = 260, H = 100, max = Math.max.apply(null, rows.map(function (r) { return r.rev; }).concat([1]));
    var pts = rows.map(function (r, i) { return [8 + i / (rows.length - 1) * (W - 16), H - 6 - r.rev / max * (H - 16)]; });
    var d = "M" + pts.map(function (p) { return p[0].toFixed(1) + " " + p[1].toFixed(1); }).join(" L");
    return '<svg class="chart" viewBox="0 0 ' + W + " " + (H + 18) + '" role="img" aria-label="High-risk revenue by days since last order"><path d="' + d + " L" + pts[pts.length - 1][0] + " " + H + " L8 " + H + ' Z" fill="currentColor" fill-opacity=".08"/>' +
      '<path class="draw" style="--len:600" d="' + d + '" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>' +
      pts.map(function (p, i) { return '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="4" fill="#F5EE50" stroke="currentColor" stroke-width="2"><title>' + label(rows[i].lo, rows[i].hi) + " days: " + inr(rows[i].rev) + "</title></circle>"; }).join("") +
      [0, 3, 6].map(function (i) { return '<text x="' + pts[i][0] + '" y="' + (H + 14) + '" text-anchor="middle">' + label(rows[i].lo, rows[i].hi) + "</text>"; }).join("") + "</svg>";
  }

  function summaryLines(S) {
    var out = [], hiShare = pc(S.tier.high, S.total);
    out.push("<b>" + hiShare + "%</b> of estimated monthly revenue (" + inr(S.tier.high) + ") comes from high-risk customers.");
    var late = S.highByRecency.filter(function (r) { return r.lo >= 60; }).reduce(function (s, r) { return s + r.rev; }, 0);
    var hiTot = S.tier.high;
    if (hiTot > 0) out.push("Of that, <b>" + pc(late, hiTot) + "%</b> is from customers who haven't ordered in 60+ days.");
    if (S.metrics) out.push("The model caught <b>" + Math.round(S.metrics.recall * 100) + "%</b> of the customers who actually left (recall).");
    else out.push("Add a <b>churned</b> column to your CSV to compare predictions with what really happened.");
    return out;
  }

  function csv(S, name) {
    var rows = [["Revenue statement (estimated monthly revenue)"], ["Dataset", name], ["Generated", new Date().toISOString()], [],
      ["Summary", "Customers", "Monthly revenue"],
      ["Total", S.n, Math.round(S.total)], ["Low risk (safe)", S.cnt.low, Math.round(S.tier.low)], ["Medium risk (watch)", S.cnt.med, Math.round(S.tier.med)], ["High risk (at risk)", S.cnt.high, Math.round(S.tier.high)], [],
      ["Revenue by tenure (months)", "Customers", "Monthly revenue"]].concat(S.byTenure.map(function (r) { return [label(r.lo, r.hi), r.n, Math.round(r.rev)]; }))
      .concat([[], ["High-risk revenue by days since last order", "Customers", "Monthly revenue"]]).concat(S.highByRecency.map(function (r) { return [label(r.lo, r.hi), r.n, Math.round(r.rev)]; }));
    return rows.map(function (r) { return r.map(function (c) { return /[",\n]/.test(String(c)) ? '"' + String(c).replace(/"/g, '""') + '"' : c; }).join(","); }).join("\n");
  }

  App.views.report = {
    render: function () {
      var b = $("body-report");
      if (!App.list) {
        b.innerHTML = '<div class="title-row"><div><h1>Report</h1><p>A revenue statement built from your customers.</p></div></div>' +
          '<div class="card light empty pop"><h3>No dataset yet</h3><p>Upload a customer file to generate the revenue statement report.</p><button class="pbtn y" type="button" data-act="goUpload">Upload a dataset</button></div>';
        return App.popIn(b);
      }
      var S = Data.statement(App.list), T = S.total || 1;
      var seg = [["low", "Safe", "var(--r-safe)"], ["med", "Watch", "var(--r-watch)"], ["high", "At risk", "#F5EE50"]];
      var sh = { low: S.cnt.low / S.n, med: S.cnt.med / S.n, high: S.cnt.high / S.n };
      var maxSh = Math.max(sh.low, sh.med, sh.high, 0.01);
      function blockH(v) { return Math.max(26, Math.round(v / maxSh * 150)); }

      b.innerHTML =
        '<div class="rep-bar pop"><button class="ibtn2" type="button" data-go="home" aria-label="Back to Home">✕</button>' +
        '<h2>Revenue Statement Report</h2><span class="rep-chip">▣ ' + esc(App.fileName) + '</span><span class="sp"></span>' +
        '<button class="ibtn2" type="button" id="rpOpen" aria-label="Open charts on Home" title="Charts">▥</button>' +
        '<button class="ibtn2" type="button" id="rpCopy" aria-label="Copy summary" title="Copy summary">⧉</button>' +
        '<button class="ibtn2" type="button" id="rpPrint" aria-label="Print" title="Print">⎙</button>' +
        '<button class="pbtn y" type="button" id="rpSave">Save report</button></div>' +

        '<div class="rs-grid"><article class="card light pop"><div class="rep-head"><h3>Revenue Statement</h3><button class="ibtn3" type="button" id="rpAll" title="Collapse or expand all" aria-label="Collapse or expand all">▤</button></div>' +
        '<div class="rs-fig">' +
        '<div><span>Total revenue</span><b class="mono">' + inr(S.total) + '</b></div>' +
        '<div><span><i style="background:var(--r-safe)"></i>Safe (low risk)</span><b class="mono">' + inr(S.tier.low) + '</b></div>' +
        '<div><span><i style="background:var(--r-watch)"></i>Watch (medium)</span><b class="mono">' + inr(S.tier.med) + '</b></div>' +
        '<div><span><i style="background:#F5EE50;box-shadow:inset 0 0 0 1px #CFC72F"></i>At risk (high)</span><b class="mono">' + inr(S.tier.high) + "</b></div></div>" +
        '<div class="rs-bar" role="img" aria-label="Revenue split: ' + pc(S.tier.low, T) + '% safe, ' + pc(S.tier.med, T) + '% watch, ' + pc(S.tier.high, T) + '% at risk">' +
        seg.map(function (x) { return '<i style="width:' + (S.tier[x[0]] / T * 100) + '%;background:' + x[2] + '"></i>'; }).join("") + "</div>" +
        '<div class="tree"><div class="t-group"><div class="t-parent"><button class="tg" type="button" aria-expanded="true" aria-label="Toggle revenue by tenure">–</button><b>Revenue by tenure</b><span class="t-amt mono">' + inr(S.total) + '</span></div><div class="t-kids">' + treeRows(S.byTenure, S.total, "months") + "</div></div>" +
        '<div class="t-group"><div class="t-parent"><button class="tg" type="button" aria-expanded="true" aria-label="Toggle high-risk revenue by recency">–</button><b>High-risk revenue by days since last order</b><span class="t-amt mono">' + inr(S.tier.high) + '</span></div><div class="t-kids">' + treeRows(S.highByRecency, S.tier.high, "days") + "</div></div></div>" +
        '<p class="sub" style="margin-top:12px">Estimated monthly revenue = average order value × orders in the last 90 days ÷ 3. This is not an accounting income statement.</p></article>' +

        '<div class="rs-col"><article class="card light pop"><div class="rep-head"><h3><span class="spark">✦</span> Assistant Summary</h3></div>' +
        '<div class="rs-sum"><div class="rs-txt">' + summaryLines(S).map(function (l) { return "<p>" + l + "</p>"; }).join("") + "</div>" +
        '<div class="trio"><div class="trio-h">' + [["Low", sh.low], ["Medium", sh.med], ["High", sh.high]].map(function (x) { return "<div><span>" + x[0] + '</span><b class="mono">' + Math.round(x[1] * 100) + "%</b></div>"; }).join("") + "</div>" +
        '<div class="trio-b"><i style="height:' + blockH(sh.low) + 'px;background:var(--r-watch)"></i><i style="height:' + blockH(sh.med) + 'px;background:var(--r-safe)"></i><i style="height:' + blockH(sh.high) + 'px;background:#F5EE50"></i></div><div class="sub" style="margin-top:6px">Share of customers by risk</div></div></div></article>' +
        '<div class="rs-two"><article class="card light pop"><h3>Revenue by tenure</h3>' + miniBars(S.byTenure) + '</article>' +
        '<article class="card light pop"><h3>High-risk revenue by recency</h3>' + miniLine(S.highByRecency) + "</article></div></div></div>";
      App.popIn(b);

      b.querySelectorAll(".tg").forEach(function (t) {
        t.addEventListener("click", function () {
          var open = t.getAttribute("aria-expanded") === "true";
          t.setAttribute("aria-expanded", String(!open)); t.textContent = open ? "+" : "–";
          t.closest(".t-group").querySelector(".t-kids").hidden = open;
        });
      });
      $("rpAll").addEventListener("click", function () {
        var tg = b.querySelectorAll(".tg"), anyOpen = Array.prototype.some.call(tg, function (t) { return t.getAttribute("aria-expanded") === "true"; });
        tg.forEach(function (t) { if ((t.getAttribute("aria-expanded") === "true") === anyOpen) t.click(); });
      });
      $("rpOpen").addEventListener("click", function () { App.show("home"); });
      $("rpPrint").addEventListener("click", function () { window.print(); });
      $("rpSave").addEventListener("click", function () {
        App.download("revenue_statement_report.csv", csv(S, App.fileName)); Store.audit("Saved revenue statement report", App.fileName); App.toast("Report saved as CSV");
      });
      $("rpCopy").addEventListener("click", function () {
        var text = "Revenue statement (" + App.fileName + ")\n" + summaryLines(S).map(function (l) { return "- " + l.replace(/<\/?b>/g, ""); }).join("\n");
        if (navigator.clipboard) navigator.clipboard.writeText(text).then(function () { App.toast("Summary copied"); }, function () { App.toast("Couldn't copy. Select the text instead."); });
        else App.toast("Couldn't copy. Select the text instead.");
      });
    }
  };
})();
