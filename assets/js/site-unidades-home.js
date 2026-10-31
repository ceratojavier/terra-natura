(function () {
  var grid = document.querySelector(".cards--units");
  if (!grid) return;

  fetch("./assets/data/unidades.json?v=20260604")
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      var units = data.unidades || [];
      var cards = grid.querySelectorAll(".card");
      units.forEach(function (u) {
        var card = Array.prototype.find.call(cards, function (el) {
          return el.querySelector('a[href*="cabanas/' + u.id + '.html"], a[href*="id=' + u.id + '"]');
        });
        if (!card) return;
        var img = card.querySelector(".card-img");
        if (img && u.foto_portada && img.getAttribute("src") !== "./" + u.foto_portada) {
          var pic = img.closest("picture");
          if (pic) {
            pic.querySelectorAll("source").forEach(function (s) {
              s.remove();
            });
          }
          img.removeAttribute("width");
          img.removeAttribute("height");
          img.src = "./" + u.foto_portada;
          img.alt = u.nombre;
        }
      });
    })
    .catch(function () {});
})();
