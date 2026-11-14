/* Opiniones: se muestran solo reseñas originales recuperadas de Google/Booking. */
(function () {
  var grid = document.querySelector("[data-resenas-grid]");
  if (!grid) return;
  var api = (window.__TN_API_BASE || "https://api.alpinasterranatura.com.ar").replace(/\/$/, "");
  function esc(value) {
    return String(value || "").replace(/[&<>"']/g, function (c) { return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]; });
  }
  function stars(score, max) {
    var count = Math.max(1, Math.min(5, Math.round(Number(score) * 5 / Number(max || 5))));
    return "★".repeat(count) + "☆".repeat(5 - count);
  }
  fetch(api + "/api/public/resenas", { cache: "no-store" }).then(function (response) {
    return response.ok ? response.json() : null;
  }).then(function (data) {
    if (!data) throw new Error("No se pudieron consultar reseñas");
    var synced = document.querySelector("[data-resenas-updated]");
    if (synced && data.actualizado) synced.textContent = "Última actualización automática: " + new Intl.DateTimeFormat("es-AR", { day: "numeric", month: "long", year: "numeric" }).format(new Date(data.actualizado + "T12:00:00")) + ".";
    ["booking", "google"].forEach(function (source) {
      var score = data[source], card = document.querySelector('[data-rep="' + source + '"]');
      if (!score || !score.puntuacion || !card) return;
      card.querySelector(".resenas-score-num").textContent = String(score.puntuacion).replace(".", ",");
      card.querySelector("[data-rep-etiqueta]").textContent = score.etiqueta || "Opiniones verificadas";
      card.querySelector("[data-rep-cantidad]").textContent = score.cantidad ? score.cantidad + " opiniones" : "Puntaje publicado";
      var starsEl = card.querySelector(".resenas-stars");
      if (starsEl) starsEl.textContent = stars(score.puntuacion, score.maximo);
      card.hidden = false;
    });
    var items = Array.isArray(data.resenas) ? data.resenas : [];
    grid.innerHTML = items.map(function (item) {
      var source = item.fuente === "booking" ? "Booking.com" : "Google Maps";
      var url = item.url || (item.fuente === "booking" ? "https://www.booking.com/reviews/ar/hotel/cabanas-alpinas-terra-natura-bialet-masse.es-ar.html" : "https://www.google.com/maps/search/?api=1&query=Caba%C3%B1as+Alpinas+Terra+Natura+Bialet+Mass%C3%A9");
      var date = item.fecha ? new Intl.DateTimeFormat("es-AR", { month: "long", year: "numeric" }).format(new Date(item.fecha.slice(0, 10) + "T12:00:00")) : "";
      return '<article class="resena-card"><div class="resena-card-head"><span class="resena-score">' + esc(item.puntaje) + '</span><div><p class="resena-label">' + stars(item.puntaje, item.maximo) + '</p><p class="resena-fuente">' + source + '</p></div></div><blockquote class="resena-texto">“' + esc(item.texto) + '”</blockquote><footer class="resena-pie">' + esc(item.autor || "Huésped verificado") + (date ? " · " + esc(date) : "") + '</footer><a class="resena-ver-fuente" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer">Ver reseña en ' + source + ' ↗</a></article>';
    }).join("");
    if (!items.length) grid.innerHTML = '<p class="muted">No hay reseñas recientes disponibles ahora. Consultá las opiniones directamente en Google y Booking.</p>';
  }).catch(function () {
    grid.innerHTML = '<p class="muted">Consultá las opiniones actuales directamente en Google y Booking.</p>';
  });
})();
