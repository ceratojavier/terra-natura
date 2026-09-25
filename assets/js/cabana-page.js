(function () {
  var params = new URLSearchParams(location.search);
  var id = params.get("id") || "alpina-1";
  var root = document.getElementById("cabana-root");
  if (!root) return;

  function ordenarFotos(u) {
    var list = (u.fotos || []).slice();
    var portada = u.foto_portada;
    if (!portada) return list;
    var out = [portada];
    list.forEach(function (src) {
      if (src !== portada && out.indexOf(src) === -1) out.push(src);
    });
    return out;
  }

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

  function buildThumbsHtml(fotos, nombre) {
    return (
      '<div class="cabana-thumbs" role="tablist" aria-label="Galería de ' +
      nombre +
      '">' +
      fotos
        .map(function (src, i) {
          var full = "./" + src;
          return (
            '<button type="button" class="cabana-thumb' +
            (i === 0 ? " is-active" : "") +
            '" role="tab" aria-selected="' +
            (i === 0 ? "true" : "false") +
            '" aria-label="Ver foto ' +
            (i + 1) +
            '" data-thumb-index="' +
            i +
            '">' +
            '<img src="' +
            full +
            '" alt="" loading="lazy" width="120" height="90" /></button>'
          );
        })
        .join("") +
      "</div>"
    );
  }

  function bindThumbs(carouselEl) {
    var thumbs = root.querySelectorAll(".cabana-thumb");
    if (!thumbs.length || !carouselEl) return;
    thumbs.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var idx = parseInt(btn.getAttribute("data-thumb-index"), 10);
        if (isNaN(idx)) return;
        var slides = carouselEl.querySelectorAll(".gallery-slide");
        var dots = carouselEl.querySelectorAll(".gallery-dot");
        slides.forEach(function (s, i) {
          s.classList.toggle("is-active", i === idx);
        });
        dots.forEach(function (d, i) {
          d.classList.toggle("is-active", i === idx);
        });
        thumbs.forEach(function (t, i) {
          t.classList.toggle("is-active", i === idx);
          t.setAttribute("aria-selected", i === idx ? "true" : "false");
        });
      });
    });
  }

  function setMeta(name, content, prop) {
    if (!content) return;
    var sel = prop ? 'meta[property="' + name + '"]' : 'meta[name="' + name + '"]';
    var el = document.querySelector(sel);
    if (!el) {
      el = document.createElement("meta");
      if (prop) el.setAttribute("property", name);
      else el.setAttribute("name", name);
      document.head.appendChild(el);
    }
    el.setAttribute("content", content);
  }

  function injectJsonLd(u, id) {
    var old = document.getElementById("cabana-jsonld");
    if (old) old.remove();
    var script = document.createElement("script");
    script.type = "application/ld+json";
    script.id = "cabana-jsonld";
    var img = u.foto_portada ? "https://alpinasterranatura.com.ar/" + u.foto_portada : "https://alpinasterranatura.com.ar/media/galeria/02-piscina.jpg";
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "VacationRental",
      name: u.nombre,
      description: u.descripcion,
      url: "https://alpinasterranatura.com.ar/cabana.html?id=" + encodeURIComponent(id),
      image: img,
      address: {
        "@type": "PostalAddress",
        addressLocality: "Bialet Massé",
        addressRegion: "Córdoba",
        addressCountry: "AR",
      },
      occupancy: { "@type": "QuantitativeValue", maxValue: u.capacidad },
    });
    document.head.appendChild(script);
  }

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
      document.title = u.nombre + " | Cabañas Terra Natura · Bialet Massé";
      var desc = (u.tagline || u.descripcion || "").slice(0, 155);
      setMeta("description", desc + " Reservá directo en Bialet Massé, sierras de Córdoba.");
      setMeta("og:title", u.nombre + " | Terra Natura", true);
      setMeta("og:description", desc, true);
      setMeta(
        "og:image",
        "https://alpinasterranatura.com.ar/" + (u.foto_portada || "media/galeria/02-piscina.jpg"),
        true
      );
      setMeta("og:url", "https://alpinasterranatura.com.ar/cabana.html?id=" + encodeURIComponent(id), true);
      injectJsonLd(u, id);

      var fotos = ordenarFotos(u);
      var carousel =
        fotos.length > 0
          ? buildCarouselHtml(fotos, u.nombre)
          : "<p class='muted'>Fotos en preparación.</p>";
      var thumbs = fotos.length > 1 ? buildThumbsHtml(fotos, u.nombre) : "";

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
        thumbs +
        (fotos.length
          ? "<p class='cabana-hint'>" +
            (fotos.length > 1
              ? fotos.length + " fotos · tocá una miniatura o usá las flechas · ampliá con un toque"
              : "Tocá la foto para verla en grande") +
            "</p>"
          : "") +
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
      bindThumbs(carouselEl);

      var s = document.createElement("script");
      s.src = "./assets/js/gallery-lightbox.js";
      document.body.appendChild(s);
    });
})();
