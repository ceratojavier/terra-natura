/* Puntaje de Booking y Google Maps: lo actualiza el servidor cada 6 h. Si no responde, queda el del HTML. */
(function () {
  var cards = document.querySelectorAll("[data-rep]");
  if (!cards.length) return;
  var base = (window.__TN_API_BASE || "https://api.alpinasterranatura.com.ar").replace(/\/$/, "");

  function numero(v) {
    return String(v).replace(".", ",");
  }

  function estrellas(p, max) {
    var n = Math.round((p / max) * 5);
    var out = "";
    for (var i = 0; i < 5; i++) out += i < n ? "★" : "☆";
    return out;
  }

  fetch(base + "/api/public/reputacion", { cache: "no-store" })
    .then(function (r) {
      return r.ok ? r.json() : null;
    })
    .then(function (data) {
      if (!data) return;
      cards.forEach(function (card) {
        var d = data[card.getAttribute("data-rep")];
        if (!d || !d.puntuacion) return;
        var num = card.querySelector(".resenas-score-num");
        var etiqueta = card.querySelector("[data-rep-etiqueta]");
        var cantidad = card.querySelector("[data-rep-cantidad]");
        var stars = card.querySelector(".resenas-stars");
        if (num) num.textContent = numero(d.puntuacion);
        if (etiqueta && d.etiqueta) etiqueta.textContent = d.etiqueta;
        if (cantidad && d.cantidad) cantidad.textContent = d.cantidad + " opiniones";
        if (stars) stars.textContent = estrellas(d.puntuacion, d.maximo || 5);
      });
    })
    .catch(function () {});
})();
