// Browser storage for the frontend-only version: dataset, prediction history, retention tasks, audit log, settings.
// When you add a backend + database, replace these calls with API requests.
(function () {
  var P = "cs_";
  function get(k, d) { try { var v = localStorage.getItem(P + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } }
  function set(k, v) { try { localStorage.setItem(P + k, JSON.stringify(v)); return true; } catch (e) { return false; } }
  function del(k) { try { localStorage.removeItem(P + k); } catch (e) {} }
  function push(k, item, cap) { var a = get(k, []); a.unshift(item); if (a.length > cap) a.length = cap; set(k, a); }
  function audit(action, detail, user) {
    user = user || (window.Auth && Auth.getUser()) || {};
    push("audit", { ts: Date.now(), user: user.email || user.name || "unknown", role: user.role || "", action: action, detail: detail || "" }, 500);
  }
  function addHistory(h) { h.ts = Date.now(); push("history", h, 500); }
  window.Store = { get: get, set: set, del: del, push: push, audit: audit, addHistory: addHistory };
})();
