(() => {
  const API = "https://api.alpinasterranatura.com.ar";
  const params = new URLSearchParams(location.search);
  const preview = params.get("tn-preview") === "1";
  const key = (() => { try { return localStorage.getItem("tn_clave") || ""; } catch { return ""; } })();
  const headers = key ? { "X-Clave": key } : {};
  const mediaUrl = (value) => value.startsWith("media/cms/") ? `${API}/api/sitio/archivo-media?ruta=${encodeURIComponent(value)}` : value;
  // La foto de frutillas es un detalle de mesa, no una foto de la pileta. Se conserva en el banco de medios,
  // pero no se presenta como foto destacada mientras el dueño elige un reemplazo desde el editor del sitio.
  const esFotoNoRepresentativa = (value) => /(?:^|\/)15-pileta-frutillas\.(?:jpe?g|webp)$/i.test(String(value || "").split("?")[0]);
  const read = (obj, path) => path.split(".").reduce((v, k) => v && v[k], obj);

  async function loadContent() {
    try {
      const endpoint = preview && key ? "/api/sitio/contenido" : "/api/sitio/contenido-publico";
      const response = await fetch(`${API}${endpoint}`, { headers, cache: "no-store" });
      if (!response.ok) return;
      const data = await response.json();
      const seo = data.home?.seo || {};
      const setMeta = (selector, value) => {
        if (typeof value !== "string" || !value.trim()) return;
        const node = document.querySelector(selector);
        if (node) node.setAttribute("content", value.trim());
      };
      if (typeof seo.title === "string" && seo.title.trim()) document.title = seo.title.trim();
      setMeta('meta[name="description"]', seo.description);
      setMeta('meta[property="og:title"]', seo.og_title || seo.title);
      setMeta('meta[property="og:description"]', seo.og_description || seo.description);
      setMeta('meta[name="twitter:title"]', seo.twitter_title || seo.og_title || seo.title);
      setMeta('meta[name="twitter:description"]', seo.twitter_description || seo.og_description || seo.description);
      document.querySelectorAll("[data-site-text]").forEach((node) => {
        const value = read(data, node.dataset.siteText);
        if (typeof value === "string" && value.trim()) node.textContent = value;
      });
      const gallery = data.home?.galeria;
      if (gallery) {
        const title = document.querySelector("#galeria h2");
        const lead = document.querySelector("#galeria .section-lead-short");
        if (title && gallery.titulo) title.textContent = gallery.titulo;
        if (lead && gallery.lead) lead.textContent = gallery.lead;
        const track = document.querySelector("#galeria .gallery-track");
        const fotosPresentables = Array.isArray(gallery?.fotos) ? gallery.fotos.filter((photo) => !esFotoNoRepresentativa(photo?.imagen)) : [];
        if (track && fotosPresentables.length) {
          const fragment = document.createDocumentFragment();
          fotosPresentables.forEach((photo, index) => {
            if (!photo || typeof photo.imagen !== "string" || !photo.imagen.trim()) return;
            const figure = document.createElement("figure");
            figure.className = "gallery-slide" + (index === 0 ? " is-active" : "");
            const image = document.createElement("img");
            image.src = mediaUrl(photo.imagen.trim());
            image.alt = typeof photo.alt === "string" ? photo.alt : "Foto de Terra Natura";
            image.loading = index === 0 ? "eager" : "lazy";
            image.decoding = "async";
            const picture = document.createElement("picture");
            picture.className = "tn-pic";
            picture.appendChild(image);
            figure.appendChild(picture);
            fragment.appendChild(figure);
          });
          if (fragment.childNodes.length) {
            track.replaceChildren(fragment);
            window.TN_refreshGalleryCarousels?.();
          }
        }
      }
      const configuredSlides = data.home?.hero_slides;
      const slidesPresentables = Array.isArray(configuredSlides) ? configuredSlides.filter((item) => !esFotoNoRepresentativa(item?.imagen)) : [];
      if (slidesPresentables.length) {
        const container = document.querySelector(".hero-slides");
        if (container) {
          const fragment = document.createDocumentFragment();
          slidesPresentables.forEach((item, index) => {
            if (typeof item?.imagen !== "string" || !item.imagen.trim()) return;
            const slide = document.createElement("span");
            slide.className = "hero-slide" + (index === 0 ? " is-active" : "");
            slide.setAttribute("role", "img");
            slide.setAttribute("aria-label", typeof item.alt === "string" ? item.alt : "Cabañas Alpinas Terra Natura");
            slide.style.backgroundImage = `url("${mediaUrl(item.imagen.trim())}")`;
            fragment.appendChild(slide);
          });
          if (fragment.childNodes.length) {
            container.replaceChildren(fragment);
            window.TN_refreshHeroSlides?.();
          }
        }
      }
      if (Array.isArray(data.unidades) && data.unidades.length) {
        const grid = document.querySelector(".cards--units");
        if (grid) {
          const fragment = document.createDocumentFragment();
          data.unidades.forEach((unit) => {
            if (!unit || !/^[a-z0-9-]+$/.test(unit.id || "") || typeof unit.nombre !== "string") return;
            const previewQuery = params.get("tn-preview") === "1" ? "?tn-preview=1" : "";
            const href = `./cabanas/${unit.id}.html${previewQuery}`;
            const card = document.createElement("article");
            card.className = "card";
            const imageLink = document.createElement("a");
            imageLink.href = href;
            const image = document.createElement("img");
            image.className = "card-img";
            image.src = mediaUrl(typeof unit.foto_portada === "string" ? unit.foto_portada : "");
            image.alt = unit.nombre;
            image.loading = "lazy";
            image.decoding = "async";
            imageLink.appendChild(image);
            card.appendChild(imageLink);
            const heading = document.createElement("h3");
            const titleLink = document.createElement("a");
            titleLink.href = href;
            titleLink.textContent = unit.nombre;
            heading.appendChild(titleLink);
            card.appendChild(heading);
            const description = document.createElement("p");
            description.textContent = typeof unit.descripcion === "string" ? unit.descripcion : "";
            card.appendChild(description);
            const list = document.createElement("ul");
            [unit.capacidad, ...(Array.isArray(unit.servicios) ? unit.servicios : [])]
              .filter((item) => typeof item === "string" && item.trim())
              .forEach((item) => {
                const li = document.createElement("li");
                li.textContent = item;
                list.appendChild(li);
              });
            card.appendChild(list);
            const detail = document.createElement("a");
            detail.className = "card-link";
            detail.href = href;
            detail.textContent = "Ver fotos y detalle →";
            card.appendChild(detail);
            fragment.appendChild(card);
          });
          if (fragment.childNodes.length) {
            grid.replaceChildren(fragment);
            grid.dataset.cmsUnitsLoaded = "true";
          }
        }
      }
      if (Array.isArray(data.home?.atracciones) && data.home.atracciones.length) {
        const grid = document.querySelector("#atracciones .attractions-grid");
        if (grid) {
          const fragment = document.createDocumentFragment();
          data.home.atracciones.forEach((place) => {
            if (!place || typeof place.titulo !== "string" || typeof place.id !== "string") return;
            const card = document.createElement("article");
            card.className = "attraction-card";
            const fotos = Array.isArray(place.fotos) ? place.fotos.filter((src) => typeof src === "string" && src.trim()) : [];
            if (fotos.length === 1) {
              const image = document.createElement("img");
              image.src = mediaUrl(fotos[0]);
              image.alt = place.titulo;
              image.loading = "lazy";
              image.decoding = "async";
              card.appendChild(image);
            } else if (fotos.length > 1) {
              const photos = document.createElement("div");
              photos.className = "attraction-card__photos";
              fotos.forEach((src) => {
                const image = document.createElement("img");
                image.src = mediaUrl(src);
                image.alt = place.titulo;
                image.loading = "lazy";
                image.decoding = "async";
                photos.appendChild(image);
              });
              card.appendChild(photos);
            }
            const title = document.createElement("h3");
            title.textContent = place.titulo;
            card.appendChild(title);
            const description = document.createElement("p");
            description.textContent = typeof place.descripcion === "string" ? place.descripcion : "";
            card.appendChild(description);
            fragment.appendChild(card);
          });
          if (fragment.childNodes.length) grid.replaceChildren(fragment);
        }
      }
      if (Array.isArray(data.home?.preguntas_frecuentes) && data.home.preguntas_frecuentes.length) {
        const list = document.querySelector("#faq .faq-list");
        const faqs = data.home.preguntas_frecuentes.filter((item) => typeof item?.pregunta === "string" && typeof item?.respuesta === "string");
        if (list && faqs.length) {
          const fragment = document.createDocumentFragment();
          faqs.forEach((item) => {
            const details = document.createElement("details");
            details.className = "faq-item";
            const question = document.createElement("summary");
            question.textContent = item.pregunta;
            const answer = document.createElement("p");
            answer.textContent = item.respuesta;
            details.append(question, answer);
            fragment.appendChild(details);
          });
          list.replaceChildren(fragment);
          const schema = document.querySelector("[data-site-faq-schema]");
          if (schema) schema.textContent = JSON.stringify({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            mainEntity: faqs.map((item) => ({
              "@type": "Question",
              name: item.pregunta,
              acceptedAnswer: { "@type": "Answer", text: item.respuesta },
            })),
          });
        }
      }
      if (Array.isArray(data.home?.resenas)) {
        const grid = document.querySelector("#resenas .resenas-grid");
        if (grid) {
          const fragment = document.createDocumentFragment();
          data.home.resenas.forEach((item) => {
            if (!item || typeof item.texto !== "string" || typeof item.titulo !== "string") return;
            const card = document.createElement("article");
            card.className = "resena-card";
            const head = document.createElement("div");
            head.className = "resena-card-head";
            const score = document.createElement("span");
            score.className = "resena-score";
            score.textContent = String(item.puntaje || "");
            score.setAttribute("aria-label", `Puntuación ${score.textContent}`);
            const meta = document.createElement("div");
            const label = document.createElement("p");
            label.className = "resena-label";
            label.textContent = String(item.etiqueta || "");
            const source = document.createElement("p");
            source.className = "resena-fuente";
            source.textContent = String(item.fuente || "");
            meta.append(label, source);
            head.append(score, meta);
            card.appendChild(head);
            const title = document.createElement("h3");
            title.className = "resena-titulo";
            title.textContent = item.titulo;
            card.appendChild(title);
            const tags = Array.isArray(item.etiquetas) ? item.etiquetas.filter((tag) => typeof tag === "string" && tag.trim()) : [];
            if (tags.length) {
              const tagList = document.createElement("div");
              tagList.className = "resena-tags";
              tags.forEach((tag) => {
                const pill = document.createElement("span");
                pill.className = "resena-tag";
                pill.textContent = tag;
                tagList.appendChild(pill);
              });
              card.appendChild(tagList);
            }
            const quote = document.createElement("blockquote");
            quote.className = "resena-texto";
            quote.textContent = `“${item.texto}”`;
            card.appendChild(quote);
            const footer = document.createElement("footer");
            footer.className = "resena-pie";
            footer.textContent = String(item.pie || "");
            card.appendChild(footer);
            fragment.appendChild(card);
          });
          grid.replaceChildren(fragment);
        }
      }
      const video = document.querySelector("[data-site-hero-video]");
      const hero = data.home?.hero || {};
      if (video) {
        const mobile = matchMedia("(max-width: 859px)").matches;
        const src = mobile ? hero.video_mobile : hero.video_desktop;
        if (src) {
          video.poster = mediaUrl(hero.video_poster || "./media/galeria/02-piscina.webp");
          video.src = mediaUrl(src);
          video.hidden = false;
          const slides = document.querySelector(".hero-slides");
          if (slides) slides.hidden = true;
          if (matchMedia("(prefers-reduced-motion: reduce)").matches || navigator.connection?.saveData) video.pause();
          else video.play().catch(() => {});
          const toggle = document.querySelector("[data-site-video-sound]");
          if (toggle) {
            toggle.hidden = false;
            toggle.addEventListener("click", () => {
              video.muted = !video.muted;
              toggle.setAttribute("aria-pressed", String(!video.muted));
              toggle.textContent = video.muted ? "Sonido apagado" : "Sonido activado";
            });
          }
        }
      }
      document.documentElement.dataset.siteContentLoaded = "true";
      if (preview && !key) document.documentElement.dataset.sitePreviewUnavailable = "true";
    } catch { /* El HTML local mantiene la versión de respaldo. */ }
  }
  loadContent();
})();
