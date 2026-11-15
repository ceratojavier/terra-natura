(function () {
  var roots = document.querySelectorAll("[data-resenas-root]");
  if (!roots.length) return;
  var api = (window.__TN_API_BASE || "https://api.alpinasterranatura.com.ar").replace(/\/$/, "");
  var links = '<p class="resenas-links"><a href="https://www.booking.com/reviews/ar/hotel/cabanas-alpinas-terra-natura-bialet-masse.es-ar.html" target="_blank" rel="noopener noreferrer">Ver todas en Booking</a> · <a href="https://www.google.com/maps/search/?api=1&query=Caba%C3%B1as+Alpinas+Terra+Natura+Bialet+Mass%C3%A9" target="_blank" rel="noopener noreferrer">Ver en Google Maps</a></p>';

  function esc(value) {
    return String(value || "").replace(/[&<>"']/g, function (char) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char];
    });
  }

  function render(root, data) {
    var items = Array.isArray(data.resenas) ? data.resenas : [];
    if (root.getAttribute("data-resenas-root") === "compact") items = items.slice(0, 3);
    var cards = items.map(function (review) {
      var source = review.fuente === "booking" ? "Booking.com" : "Google Maps";
      var score = Number(review.puntaje || 0);
      var max = Number(review.maximo || 5);
      var stars = Math.max(1, Math.min(5, Math.round(score * 5 / max)));
      var url = review.url || (review.fuente === "booking" ? "https://www.booking.com/reviews/ar/hotel/cabanas-alpinas-terra-natura-bialet-masse.es-ar.html" : "https://www.google.com/maps/search/?api=1&query=Caba%C3%B1as+Alpinas+Terra+Natura+Bialet+Mass%C3%A9");
      return '<article class="resena-card"><div class="resena-card-head"><span class="resena-score">' + esc(score) + '</span><div><p class="resena-label">' + "★".repeat(stars) + '</p><p class="resena-fuente">' + source + '</p></div></div><blockquote class="resena-texto">“' + esc(review.texto) + '”</blockquote><footer class="resena-pie">' + esc(review.autor || "Huésped verificado") + (review.fecha ? " · " + esc(review.fecha.slice(0, 10)) : "") + '</footer><a href="' + esc(url) + '" target="_blank" rel="noopener noreferrer">Ver reseña en ' + source + ' ↗</a></article>';
    });
    root.innerHTML = (cards.length ? '<div class="resenas-grid">' + cards.join("") + '</div>' : '<p class="muted">No hay reseñas verificadas disponibles en este momento.</p>') + links;
  }

  fetch(api + "/api/public/resenas", { cache: "no-store" })
    .then(function (response) { return response.ok ? response.json() : Promise.reject(new Error("No se pudo consultar la reputación")); })
    .then(function (data) { roots.forEach(function (root) { render(root, data); }); })
    .catch(function () {
      roots.forEach(function (root) {
        root.innerHTML = '<p class="muted">Consultá las opiniones directamente en Google y Booking.</p>' + links;
      });
    });
})();
