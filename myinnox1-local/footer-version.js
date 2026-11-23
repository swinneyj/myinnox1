// Fills the footer with the build identifier so users can quote it in bug reports.
(function () {
  var el = document.getElementById("app-version");
  if (!el) return;
  var v = window.APP_VERSION || {};
  var text = "InnoStudio · Private Edition";
  el.textContent = text;
  el.title = text;
  el.hidden = false;
})();
