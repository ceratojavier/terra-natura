(function () {
  var params = new URLSearchParams(location.search);
  var id = params.get("id") || "alpina-1";
  var root = document.getElementById("cabana-root");
  if (!root) return;

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
      document.title = u.nombre + " | Terra Natura";

      var fotos = (u.fotos || [])
        .map(function (src, i) {
          return (
            '<figure class="cabana-gallery-item' +
            (i === 0 ? " cabana-gallery-item--main" : "") +
            '">' +
            '<img src="./' +
            src +
            '" alt="' +
            u.nombre +
            " " +
            (i + 1) +
            '" loading="lazy" data-lightbox="./' +
            src +
            '" /></figure>'
          );
        })
        .join("");

      var am = (u.amenities || [])
        .map(function (a) {
          return "<li>" + a + "</li>";
        })
        .join("");

      root.innerHTML =
        '<nav class="breadcrumb"><a href="./index.html">Inicio</a> · <a href="./index.html#unidades">Cabañas</a> · ' +
        u.nombre +
        "</nav>" +
        "<h1>" +
        u.nombre +
        "</h1>" +
        "<p class='muted'>Hasta " +
        u.capacidad +
        " personas · ideal " +
        u.recomendado +
        "</p>" +
        '<div class="cabana-gallery" data-gallery>' +
        fotos +
        "</div>" +
        "<p class='cabana-hint'>Tocá una foto para verla en grande</p>" +
        "<p>" +
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
        encodeURIComponent("Hola, consulto por " + u.nombre) +
        '" target="_blank" rel="noopener">WhatsApp</a>' +
        "</div>";

      var s = document.createElement("script");
      s.src = "./assets/js/gallery-lightbox.js";
      document.body.appendChild(s);
    });
})();
