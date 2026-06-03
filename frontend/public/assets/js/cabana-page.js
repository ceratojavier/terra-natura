(function () {
  var params = new URLSearchParams(location.search);
  var id = params.get("id") || "alpina-1";
  var root = document.getElementById("cabana-root");
  if (!root) return;

  function buildCarouselHtml(fotos, nombre) {
    var slides = fotos
      .map(function (src, i) {
        var full = "./" + src;
        return (
          '<figure class="gallery-slide' +
          (i === 0 ? " is-active" : "") +
          '">' +
          '<img src="' +
          full +
          '" alt="' +
          nombre +
          " — foto " +
          (i + 1) +
          '" loading="' +
          (i === 0 ? "eager" : "lazy") +
          '" data-lightbox="' +
          full +
          '" /></figure>'
        );
      })
      .join("");

    return (
      '<div class="gallery-carousel cabana-unit-carousel" data-gallery-carousel>' +
      '<button class="gallery-nav gallery-nav--prev" type="button" aria-label="Foto anterior">‹</button>' +
      '<div class="gallery-track">' +
      slides +
      "</div>" +
      '<button class="gallery-nav gallery-nav--next" type="button" aria-label="Foto siguiente">›</button>' +
      '<div class="gallery-dots" aria-label="Fotos de la unidad"></div>' +
      "</div>"
    );
  }

  fetch("./assets/data/unidades.json")
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      var u = (data.unidades || []).find(function (x) {
        return x.id === id;
      });
      if (!u) {
        root.innerHTML = "<p>Unidad no encontrada. <a href='./index.html#unidades'>Ver todas</a></p>";
        return;
      }
      document.title = u.nombre + " | Cabañas Terra Natura";

      var fotos = u.fotos || [];
      var carousel =
        fotos.length > 0
          ? buildCarouselHtml(fotos, u.nombre)
          : "<p class='muted'>Fotos en preparación.</p>";

      var am = (u.amenities || [])
        .map(function (a) {
          return "<li>" + a + "</li>";
        })
        .join("");

      var tagline = u.tagline ? "<p class='cabana-tagline'>" + u.tagline + "</p>" : "";

      root.innerHTML =
        '<nav class="breadcrumb"><a href="./index.html">Inicio</a> · <a href="./index.html#unidades">Cabañas</a> · ' +
        u.nombre +
        "</nav>" +
        "<h1>" +
        u.nombre +
        "</h1>" +
        tagline +
        "<p class='muted'>Hasta " +
        u.capacidad +
        " personas · recomendado " +
        u.recomendado +
        " adultos</p>" +
        carousel +
        (fotos.length ? "<p class='cabana-hint'>Deslizá o usá las flechas · tocá una foto para verla en grande</p>" : "") +
        "<p class='cabana-description'>" +
        u.descripcion +
        "</p>" +
        "<ul class='amenities-list'>" +
        am +
        "</ul>" +
        '<div class="cta-row">' +
        '<a class="btn btn-primary" href="./reservar.html?unidad=' +
        encodeURIComponent(u.id) +
        '">Cotizar y reservar online</a>' +
        '<a class="btn btn-outline" href="https://wa.me/5493541571190?text=' +
        encodeURIComponent("Hola, me interesa " + u.nombre + " en Terra Natura. ¿Tenés disponibilidad?") +
        '" target="_blank" rel="noopener">WhatsApp</a>' +
        "</div>";

      var carouselEl = root.querySelector("[data-gallery-carousel]");
      if (carouselEl && window.TN_initGalleryCarousel) {
        window.TN_initGalleryCarousel(carouselEl);
      }

      var s = document.createElement("script");
      s.src = "./assets/js/gallery-lightbox.js";
      document.body.appendChild(s);
    });
})();
