(function () {
  var roots = document.querySelectorAll("[data-resenas-root]");
  if (!roots.length) return;

  function esc(s) {
    if (!s) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function estrellas(p, max) {
    var n = Math.round((p / max) * 5);
    var out = "";
    for (var i = 0; i < 5; i++) {
      out += i < n ? "★" : "☆";
    }
    return out;
  }

  function fuenteLabel(fuente) {
    if (fuente === "google_maps") return "Google Maps";
    if (fuente === "booking") return "Booking.com";
    return fuente;
  }

  function renderResumen(fuentes) {
    var b = fuentes.booking;
    var g = fuentes.google_maps;
    return (
      '<div class="resenas-resumen">' +
      '<div class="resenas-score-card">' +
      '<span class="resenas-score-num">' +
      b.puntuacion +
      "</span>" +
      '<span class="resenas-score-meta"><strong>' +
      esc(b.etiqueta) +
      "</strong> en " +
      esc(b.nombre) +
      "<br /><span class='muted'>" +
      b.cantidad +
      " opiniones verificadas</span></span>" +
      "</div>" +
      '<div class="resenas-score-card resenas-score-card--google">' +
      '<span class="resenas-score-num resenas-score-num--google">' +
      g.puntuacion +
      "</span>" +
      '<span class="resenas-score-meta"><strong>' +
      esc(g.etiqueta) +
      "</strong> en " +
      esc(g.nombre) +
      '<br /><span class="resenas-stars" aria-hidden="true">' +
      estrellas(g.puntuacion, g.maximo) +
      "</span></span>" +
      "</div>" +
      "</div>"
    );
  }

  function renderCard(r) {
    var tags = [];
    if (r.tipo_viaje) tags.push(r.tipo_viaje);
    if (r.estadia) tags.push(r.estadia);
    var tagsHtml = tags
      .map(function (t) {
        return '<span class="resena-tag">' + esc(t) + "</span>";
      })
      .join("");

    return (
      '<article class="resena-card">' +
      '<div class="resena-card-head">' +
      '<span class="resena-score" aria-label="Puntuación ' +
      r.puntuacion +
      ' de ' +
      r.maximo +
      '">' +
      r.puntuacion +
      "</span>" +
      '<div><p class="resena-label">' +
      esc(r.etiqueta_puntuacion) +
      "</p>" +
      '<p class="resena-fuente">' +
      esc(fuenteLabel(r.fuente)) +
      "</p></div></div>" +
      (r.titulo ? "<h3 class='resena-titulo'>" + esc(r.titulo) + "</h3>" : "") +
      (tagsHtml ? '<div class="resena-tags">' + tagsHtml + "</div>" : "") +
      '<blockquote class="resena-texto">“' +
      esc(r.texto) +
      "”</blockquote>" +
      '<footer class="resena-pie">' +
      esc(r.autor) +
      (r.origen ? " · " + esc(r.origen) : "") +
      "</footer></article>"
    );
  }

  function render(root, data) {
    var compact = root.getAttribute("data-resenas-root") === "compact";
    var list = data.resenas || [];
    if (compact) list = list.slice(0, 3);

    var links =
      '<p class="resenas-links">' +
      '<a href="' +
      esc(data.fuentes.booking.url) +
      '" target="_blank" rel="noopener noreferrer">Ver todas en Booking</a>' +
      " · " +
      '<a href="' +
      esc(data.fuentes.google_maps.url) +
      '" target="_blank" rel="noopener noreferrer">Ver en Google Maps</a>' +
      "</p>";

    root.innerHTML =
      renderResumen(data.fuentes) +
      '<div class="resenas-grid">' +
      list.map(renderCard).join("") +
      "</div>" +
      links;
  }

  fetch("./assets/data/resenas.json?v=20260604")
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      roots.forEach(function (root) {
        render(root, data);
      });
    })
    .catch(function () {
      roots.forEach(function (root) {
        root.innerHTML =
          '<p class="muted">Opiniones de huéspedes en <a href="https://www.booking.com/hotel/ar/cabanas-alpinas-terra-natura-bialet-masse.es.html" target="_blank" rel="noopener">Booking</a> y <a href="https://www.google.com/maps/search/?api=1&query=Caba%C3%B1as+Alpinas+Terra+Natura+Bialet+Mass%C3%A9" target="_blank" rel="noopener">Google Maps</a>.</p>';
      });
    });
})();
