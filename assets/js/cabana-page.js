(function () {
  var params = new URLSearchParams(location.search);
  var root = document.getElementById("cabana-root");
  if (!root) return;
  var id = params.get("id") || root.dataset.unitId || "alpina-1";
  var API = "https://api.alpinasterranatura.com.ar";
  var assetBase = location.pathname.indexOf("/cabanas/") >= 0 ? "../" : "./";
  var preview = params.get("tn-preview") === "1";
  var apiHeaders = {};
  if (preview) {
    try {
      var clave = localStorage.getItem("tn_clave") || "";
      if (clave) apiHeaders["X-Clave"] = clave;
    } catch (_) { /* Vista pública si el navegador no permite localStorage. */ }
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function assetUrl(value) {
    var clean = String(value || "").replace(/^\.\//, "");
    if (/^https?:\/\//i.test(clean)) return clean;
    if (clean.indexOf("media/cms/") === 0) return API + "/api/sitio/archivo-media?ruta=" + encodeURIComponent(clean);
    return assetBase + clean.replace(/^\//, "");
  }

  function absoluteAssetUrl(value) {
    return new URL(assetUrl(value), location.href).href;
  }

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
        var full = assetUrl(src);
        return (
          '<figure class="gallery-slide' +
          (i === 0 ? " is-active" : "") +
          '">' +
          '<img src="' +
          escapeHtml(full) +
          '" alt="' +
          escapeHtml(nombre) +
          " — foto " +
          (i + 1) +
          '" loading="' +
          (i === 0 ? "eager" : "lazy") +
          '" data-lightbox="' +
          escapeHtml(full) +
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
      escapeHtml(nombre) +
      '">' +
      fotos
        .map(function (src, i) {
          var full = assetUrl(src);
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
            escapeHtml(full) +
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
    var script = document.querySelector('script[type="application/ld+json"]');
    if (!script) script = document.createElement("script");
    script.type = "application/ld+json";
    script.id = "cabana-jsonld";
    var img = u.foto_portada ? absoluteAssetUrl(u.foto_portada) : "https://alpinasterranatura.com.ar/media/galeria/02-piscina.jpg";
    var jsonLd;
    try { jsonLd = script.textContent ? JSON.parse(script.textContent) : null; } catch { jsonLd = null; }
    var graph = jsonLd && Array.isArray(jsonLd["@graph"]) ? jsonLd["@graph"] : jsonLd ? [jsonLd] : [];
    var entity = graph.find(function (item) { return ["Accommodation", "VacationRental", "LodgingBusiness"].some(function (type) { return item["@type"] === type || Array.isArray(item["@type"]) && item["@type"].includes(type); }); });
    if (entity) {
      entity.name = u.nombre;
      entity.description = u.descripcion;
      entity.image = [img];
      entity.url = "https://alpinasterranatura.com.ar/cabanas/" + encodeURIComponent(id) + ".html";
      entity.occupancy = { "@type": "QuantitativeValue", maxValue: u.capacidad };
      jsonLd["@graph"] = graph;
      script.textContent = JSON.stringify(jsonLd);
    } else {
      script.textContent = JSON.stringify({
        "@context": "https://schema.org",
        "@type": "VacationRental",
        name: u.nombre,
        description: u.descripcion,
        url: "https://alpinasterranatura.com.ar/cabanas/" + encodeURIComponent(id) + ".html",
        image: img,
        address: { "@type": "PostalAddress", addressLocality: "Bialet Massé", addressRegion: "Córdoba", addressCountry: "AR" },
        occupancy: { "@type": "QuantitativeValue", maxValue: u.capacidad },
      });
    }
    if (!script.isConnected) document.head.appendChild(script);
  }

  var NOMBRE_TIPO = { alpina: "Cabaña Alpina", suite: "Suite loft" };

  function unidadPorTipo(lista, tipo) {
    var delTipo = lista.filter(function (x) {
      return x.tipo === tipo;
    });
    if (!delTipo.length) return null;
    var base = delTipo[0];
    var fotos = [];
    delTipo.forEach(function (x) {
      ordenarFotos(x).forEach(function (src) {
        if (fotos.indexOf(src) === -1) fotos.push(src);
      });
    });
    return Object.assign({}, base, {
      id: base.id,
      nombre: NOMBRE_TIPO[tipo] || base.nombre.replace(/\s*\d+$/, ""),
      fotos: fotos.slice(0, 14),
    });
  }

  Promise.all([
    fetch(assetBase + "assets/data/unidades.json", { cache: "no-cache" }).then(function (r) { return r.json(); }),
    fetch(API + (preview && apiHeaders["X-Clave"] ? "/api/sitio/contenido" : "/api/sitio/contenido-publico"), { headers: apiHeaders, cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }),
  ])
    .then(function (responses) {
      var data = responses[0];
      var cms = responses[1];
      var tipo = params.get("tipo");
      var u = tipo
        ? unidadPorTipo(data.unidades || [], tipo)
        : (data.unidades || []).find(function (x) {
            return x.id === id;
          });
      if (!u) {
        root.innerHTML = "<p>Unidad no encontrada. <a href='" + assetBase + "index.html#unidades'>Ver todas</a></p>";
        return;
      }
      var cmsUnidad = cms && Array.isArray(cms.unidades) ? cms.unidades.find(function (x) { return x.id === u.id; }) : null;
      if (cmsUnidad) {
        u = Object.assign({}, u, {
          nombre: cmsUnidad.nombre || u.nombre,
          tagline: cmsUnidad.tagline || u.tagline,
          descripcion: cmsUnidad.descripcion || u.descripcion,
          foto_portada: cmsUnidad.foto_portada || u.foto_portada,
          fotos: Array.isArray(cmsUnidad.fotos) && cmsUnidad.fotos.length ? cmsUnidad.fotos : u.fotos,
          amenities: Array.isArray(cmsUnidad.amenities) ? cmsUnidad.amenities : u.amenities,
        });
      }
      document.title = u.nombre + " | Cabañas Alpinas Terra Natura · Bialet Massé";
      var desc = (u.tagline || u.descripcion || "").slice(0, 155);
      setMeta("description", desc + " Reservá directo en Bialet Massé, sierras de Córdoba.");
      setMeta("og:title", u.nombre + " | Cabañas Alpinas Terra Natura", true);
      setMeta("og:description", desc, true);
      setMeta(
        "og:image",
        absoluteAssetUrl(u.foto_portada || "media/galeria/02-piscina.jpg"),
        true
      );
      setMeta("og:url", "https://alpinasterranatura.com.ar/cabanas/" + encodeURIComponent(u.id) + ".html", true);
      injectJsonLd(u, id);

      var fotos = ordenarFotos(u);
      var carousel =
        fotos.length > 0
          ? buildCarouselHtml(fotos, u.nombre)
          : "<p class='muted'>Fotos en preparación.</p>";
      var thumbs = fotos.length > 1 ? buildThumbsHtml(fotos, u.nombre) : "";

      var am = (u.amenities || [])
        .map(function (a) {
          return "<li>" + escapeHtml(a) + "</li>";
        })
        .join("");

      var tagline = u.tagline ? "<p class='cabana-tagline'>" + escapeHtml(u.tagline) + "</p>" : "";

      root.innerHTML =
        '<nav class="breadcrumb"><a href="' + assetBase + 'index.html' + (preview ? '?tn-preview=1' : '') + '">Inicio</a> · <a href="' + assetBase + 'index.html' + (preview ? '?tn-preview=1' : '') + '#unidades">Cabañas</a> · ' +
        escapeHtml(u.nombre) +
        "</nav>" +
        "<h1>" +
        escapeHtml(u.nombre) +
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
        escapeHtml(u.descripcion) +
        "</p>" +
        "<ul class='amenities-list'>" +
        am +
        "</ul>" +
        '<div class="cta-row">' +
        '<a class="btn btn-primary" href="' + assetBase + 'reservar.html?unidad=' +
        encodeURIComponent(u.id) +
        '">Cotizar y reservar online</a>' +
        '<a class="btn btn-outline" href="https://wa.me/5493541571190?text=' +
        encodeURIComponent(
          "Hola, me interesa la " + u.nombre + ". ¿Tienen disponibilidad? (TN-CABANA-" + (tipo || u.id) + ")"
        ) +
        '" target="_blank" rel="noopener">WhatsApp</a>' +
        "</div>";

      var carouselEl = root.querySelector("[data-gallery-carousel]");
      if (carouselEl && window.TN_initGalleryCarousel) {
        window.TN_initGalleryCarousel(carouselEl);
      }
      bindThumbs(carouselEl);

      var s = document.createElement("script");
      s.src = assetBase + "assets/js/gallery-lightbox.js";
      document.body.appendChild(s);
    });
})();
