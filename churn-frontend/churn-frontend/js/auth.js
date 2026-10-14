// Frontend-only session helper. The user is kept in localStorage so the dashboard can greet them.
// NOTE: this is not secure authentication or real access control. With a backend, verify the Google
// ID token there and store roles in your database.
(function () {
  var KEY = "churnsight_user";
  var ROLES = ["viewer", "analyst", "admin"];

  function getUser() { try { return JSON.parse(localStorage.getItem(KEY)); } catch (e) { return null; } }
  function setUser(u) { if (u && ROLES.indexOf(u.role) < 0) u.role = "analyst"; try { localStorage.setItem(KEY, JSON.stringify(u)); } catch (e) {} }
  function signOut() {
    if (window.Store) Store.audit("Signed out", "");
    try { localStorage.removeItem(KEY); } catch (e) {}
    location.href = "index.html";
  }
  function requireAuth() {
    var u = getUser();
    if (!u) { location.replace("login.html"); return null; }
    if (ROLES.indexOf(u.role) < 0) { u.role = "analyst"; setUser(u); }
    return u;
  }
  // viewer: read only. analyst: can upload/predict/manage tasks. admin: also settings and the audit log.
  function can(action) {
    var u = getUser() || {}, r = u.role || "analyst";
    if (action === "write") return r !== "viewer";
    if (action === "settings" || action === "audit") return r === "admin";
    return true;
  }
  function decodeJwt(token) {
    var part = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    var json = decodeURIComponent(atob(part).split("").map(function (c) { return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2); }).join(""));
    return JSON.parse(json);
  }
  window.Auth = { ROLES: ROLES, getUser: getUser, setUser: setUser, signOut: signOut, requireAuth: requireAuth, can: can, decodeJwt: decodeJwt };
})();
