/* Páginas internas viejas: solo el dueño. Pide usuario y clave una vez por aparato (la misma del programa /app)
   y la agrega a cada pedido al motor. */
(function () {
  var API = (window.__TN_API_BASE || "https://api.alpinasterranatura.com.ar").replace(/\/$/, "");
  function clave() {
    try { return localStorage.getItem("tn_clave") || ""; } catch (e) { return ""; }
  }
  function usuario() {
    try { return localStorage.getItem("tn_usuario") || ""; } catch (e) { return ""; }
  }

  var fetchOriginal = window.fetch.bind(window);
  window.fetch = function (input, init) {
    var url = typeof input === "string" ? input : (input && input.url) || "";
    if (url.indexOf("/api/") !== -1 && clave()) {
      init = init || {};
      var h = new Headers(init.headers || (typeof input !== "string" && input.headers) || {});
      if (!h.has("X-Clave")) h.set("X-Clave", clave());
      init.headers = h;
    }
    return fetchOriginal(input, init);
  };

  if (clave() && usuario()) return;
  document.documentElement.style.visibility = "hidden";

  function mostrar() {
    document.documentElement.style.visibility = "";
    var capa = document.createElement("div");
    capa.setAttribute("style", "position:fixed;inset:0;z-index:99999;background:#0f1f18;display:grid;place-items:center;font-family:system-ui,sans-serif");
    capa.innerHTML =
      '<form style="background:#16261f;border:1px solid #2f4a3d;border-radius:16px;padding:24px;width:min(340px,90vw);color:#f8fafc">' +
      '<p style="font-weight:700;font-size:18px;margin:0 0 8px">Terra Natura · Entrar</p>' +
      '<p style="font-size:13px;opacity:.75;margin:0 0 14px">Página interna del dueño.</p>' +
      '<input name="u" placeholder="Usuario" autocomplete="username" autocapitalize="none" style="width:100%;box-sizing:border-box;padding:12px;margin-bottom:10px;border-radius:10px;border:1px solid #475569;background:#0b1410;color:#fff">' +
      '<input name="c" type="password" placeholder="Clave" autocomplete="current-password" style="width:100%;box-sizing:border-box;padding:12px;margin-bottom:12px;border-radius:10px;border:1px solid #475569;background:#0b1410;color:#fff">' +
      '<button style="width:100%;padding:12px;border:0;border-radius:10px;background:#d8b85a;color:#0f1f18;font-weight:700">Entrar</button>' +
      '<p data-err style="color:#fda4af;font-size:12px;margin:10px 0 0"></p></form>';
    document.body.appendChild(capa);
    var form = capa.querySelector("form");
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var u = form.u.value.trim().toLowerCase();
      var c = form.c.value.trim();
      fetchOriginal(API + "/api/programa/config/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario: u, clave: c }),
      }).then(function (r) {
        if (!r.ok) throw new Error();
        localStorage.setItem("tn_clave", c);
        localStorage.setItem("tn_usuario", u);
        window.location.reload();
      }).catch(function () {
        form.querySelector("[data-err]").textContent = "Usuario o clave incorrectos.";
      });
    });
  }
  if (document.body) mostrar();
  else document.addEventListener("DOMContentLoaded", mostrar);
})();
