// Light / dark theme. Loaded in <head> so the saved theme is applied before the page paints.
// Any element with data-theme-toggle switches the theme. Light is the default.
(function () {
  var KEY = "cs_theme", root = document.documentElement;
  function read() { try { var v = localStorage.getItem(KEY); return v === "dark" || v === "light" ? v : null; } catch (e) { return null; } }
  function current() { return root.getAttribute("data-theme") === "dark" ? "dark" : "light"; }

  // Keep every toggle in the page in step with the current theme
  function sync() {
    var dark = current() === "dark", els = document.querySelectorAll("[data-theme-toggle]");
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (el.getAttribute("role") === "switch") { el.setAttribute("aria-checked", String(dark)); continue; }
      var label = dark ? "Switch to light mode" : "Switch to dark mode";
      el.setAttribute("aria-label", label); el.setAttribute("title", label);
      var ic = el.querySelector(".ti"); if (ic) ic.textContent = dark ? "☀︎" : "☾";
    }
  }
  function set(t) {
    root.setAttribute("data-theme", t === "dark" ? "dark" : "light");
    try { localStorage.setItem(KEY, current()); } catch (e) {}
    sync(); window.dispatchEvent(new Event("themechange"));
  }

  root.setAttribute("data-theme", read() || "light");
  window.Theme = { get: current, set: set, toggle: function () { set(current() === "dark" ? "light" : "dark"); } };
  document.addEventListener("DOMContentLoaded", sync);
  document.addEventListener("click", function (e) { if (e.target.closest("[data-theme-toggle]")) window.Theme.toggle(); });
})();
