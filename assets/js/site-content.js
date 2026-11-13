(() => {
  const API = "https://api.alpinasterranatura.com.ar";
  const params = new URLSearchParams(location.search);
  const preview = params.get("tn-preview") === "1";
  const editorPreview = params.has("tn-editor-preview");
  const key = (() => { try { return localStorage.getItem("tn_clave") || ""; } catch { return ""; } })();
  const headers = key ? { "X-Clave": key } : {};
  const mediaUrl = (value) => String(value || "").startsWith("media/cms/") ? `${API}/api/sitio/archivo-media?ruta=${encodeURIComponent(value)}` : value;
  // La foto de frutillas es un detalle de mesa, no una foto de la pileta. Se conserva en el banco de medios,
  // pero no se presenta como foto destacada mientras el dueño elige un reemplazo desde el editor del sitio.
  const esFotoNoRepresentativa = (value) => /(?:^|\/)15-pileta-frutillas\.(?:jpe?g|webp)$/i.test(String(value || "").split("?")[0]);
  const read = (obj, path) => path.split(".").reduce((v, k) => v && v[k], obj);
  const mergeContent = (base, override) => {
    if (!base || typeof base !== "object" || Array.isArray(base) || !override || typeof override !== "object" || Array.isArray(override)) {
      return override === undefined ? base : override;
    }
    const merged = { ...base };
    Object.entries(override).forEach(([name, value]) => {
      merged[name] = value && typeof value === "object" && !Array.isArray(value)
        ? mergeContent(base[name], value)
        : value;
    });
    return merged;
  };
  const addEditorAction = (container, field, label, className = "tn-editor-action") => {
    if (!editorPreview || !container) return null;
    const existing = container.querySelector(`[data-tn-editor-action="${field}"]`);
    if (existing) return existing;
    const button = document.createElement("button");
    button.type = "button";
    button.className = className;
    button.textContent = label;
    button.dataset.siteEditorKey = field;
    button.dataset.tnEditorAction = field;
    button.setAttribute("data-tn-preview-control", "true");
    button.style.cssText = "position:absolute;z-index:80;top:12px;right:12px;border:1px solid #0b764a;border-radius:999px;background:#fff;color:#0b3c29;padding:7px 11px;font:600 12px system-ui;box-shadow:0 4px 16px #0003;cursor:pointer";
    container.appendChild(button);
    if (getComputedStyle(container).position === "static") container.style.position = "relative";
    return button;
  };

  // Estos campos se marcan desde el HTML, antes de consultar la API. Así el
  // editor sigue abriendo los títulos aunque el CMS del servidor todavía no
  // conozca la estructura editorial nueva.
  const editorialRows = [
    ["alpinas", "cabanas-alpinas"],
    ["suite-5", "suite-planta-alta"],
    ["suite-4", "suite-planta-baja"],
  ];
  const bindEditorialFields = (editorial) => {
    const heading = document.querySelector("#unidades .tn-editorial-heading h2");
    const lead = document.querySelector("#unidades .tn-editorial-heading p");
    if (heading) heading.dataset.siteEditorKey = "home.unidades_editoriales.titulo";
    if (lead) lead.dataset.siteEditorKey = "home.unidades_editoriales.lead";
    editorialRows.forEach(([id, htmlId], index) => {
      const row = document.getElementById(htmlId);
      if (!row) return;
      const card = editorial?.cards?.find?.((item) => item?.id === id) || editorial?.cards?.[index];
      const key = `home.unidades_editoriales.cards.${index}`;
      const eyebrow = row.querySelector(".tn-stay-kicker");
      const title = row.querySelector("h3");
      const description = row.querySelector(".tn-stay-copy > p");
      const image = row.querySelector(".tn-stay-visual img");
      const galleryTrigger = row.querySelector("[data-open-photo-gallery]");
      if (eyebrow) eyebrow.dataset.siteEditorKey = `${key}.eyebrow`;
      if (title) title.dataset.siteEditorKey = `${key}.titulo`;
      if (description) description.dataset.siteEditorKey = `${key}.texto`;
      // En edición, tocar la foto grande abre el organizador de la galería
      // completa de esa unidad, no el selector aislado de portada.
      if (image) image.dataset.siteEditorKey = editorPreview ? `${key}.fotos.0` : `${key}.imagen`;
      if (galleryTrigger && editorPreview) galleryTrigger.dataset.siteEditorKey = `${key}.fotos.0`;
      const list = row.querySelector(".tn-feature-list");
      if (list) [...list.children].forEach((item, bulletIndex) => {
        item.dataset.siteEditorKey = `${key}.bullets.${bulletIndex}`;
      });
      if (!card) return;
      if (eyebrow && typeof card.eyebrow === "string") eyebrow.textContent = card.eyebrow;
      if (title && typeof card.titulo === "string") title.textContent = card.titulo;
      if (description && typeof card.texto === "string") description.textContent = card.texto;
      if (list && Array.isArray(card.bullets)) [...list.children].forEach((item, bulletIndex) => {
        if (typeof card.bullets[bulletIndex] === "string") item.textContent = card.bullets[bulletIndex];
      });
      if (image && typeof card.imagen === "string" && card.imagen.trim()) image.src = mediaUrl(card.imagen.trim());
    });
  };
  bindEditorialFields();

  if (editorPreview) {
    // Los videos no siempre están dentro de un botón. Marcarlos directamente
    // permite abrir el selector al tocar el video en la vista previa.
    document.querySelector(".hero-video")?.setAttribute("data-site-editor-key", "home.hero.video_desktop");
    document.querySelector(".hero-video-backdrop")?.setAttribute("data-site-editor-key", "home.hero.video_mobile");
    document.querySelector("#tn-video-dialog video")?.setAttribute("data-site-editor-key", "home.video_galeria");
    document.querySelector(".tn-guide-film__video")?.setAttribute("data-site-editor-key", "home.video_guia");
    const hero = document.querySelector(".hero");
    if (hero) {
      const toolbar = document.createElement("div");
      toolbar.dataset.tnPreviewControl = "hero-media-toolbar";
      toolbar.style.cssText = "position:absolute;z-index:2147483000;top:82px;right:14px;display:flex;flex-wrap:wrap;gap:7px;max-width:min(94vw,620px);justify-content:flex-end;pointer-events:auto";
      hero.appendChild(toolbar);
      [
        ["home.hero.video_desktop", "🎬 Cambiar video PC"],
        ["home.hero.video_mobile", "📱 Cambiar video celular"],
        ["home.hero_slides.3.imagen", "＋ Agregar foto de portada"],
      ].forEach(([field, label]) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = label;
        button.dataset.siteEditorKey = field;
        button.dataset.tnPreviewControl = "true";
        button.style.cssText = "position:relative;z-index:2147483000;pointer-events:auto;border:1px solid #0b764a;border-radius:999px;background:#fff;color:#0b3c29;padding:9px 13px;font:700 13px system-ui;box-shadow:0 4px 16px #0003;cursor:pointer";
        toolbar.appendChild(button);
      });
    }
    const galleryHeader = document.querySelector("#fotos .tn-editorial-heading");
    addEditorAction(galleryHeader, "home.galeria.fotos.13.imagen", "＋ Agregar recuadro de foto");
    document.querySelectorAll("[data-open-video]").forEach((button) => {
      button.dataset.siteEditorKey = "home.video_galeria";
      button.setAttribute("aria-label", "Editar video de la galería");
      button.setAttribute("title", "Tocá para cambiar el video del complejo");
      const label = button.querySelector("small, span:last-child");
      if (label) label.textContent = "Cambiar video del complejo";
    });
    // El recuadro de presentación también ofrece un acceso visible al selector;
    // así no depende de que el clic llegue al video de fondo del lightbox.
    addEditorAction(document.querySelector(".tn-about-video"), "home.video_galeria", "🎬 Cambiar video del complejo");
    addEditorAction(document.querySelector(".tn-guide-film"), "home.video_guia", "🎬 Cambiar video de esta sección");
  }

  if (editorPreview) {
    // Activar interacción antes de cargar datos para permitir editar incluso si la API demora/falla.
    document.documentElement.classList.add("tn-site-editor-preview");
    const style = document.createElement("style");
    style.textContent = `.tn-site-editor-preview [data-site-editor-key]:not(img):not(video):not(button):not([data-tn-editor-action]),.tn-site-editor-preview [data-site-text]{cursor:pointer!important;outline:1px dashed rgba(255,214,133,.82);outline-offset:3px;-webkit-user-select:none;user-select:none;white-space:pre-wrap;resize:horizontal;overflow:auto;max-width:100%;box-sizing:border-box}.tn-site-editor-preview #unidades .tn-editorial-heading{resize:horizontal;overflow:auto;min-width:0;max-width:100%;outline:1px dashed rgba(255,214,133,.82);outline-offset:3px;box-sizing:border-box}.tn-site-editor-preview [data-site-editor-key]:hover,.tn-site-editor-preview [data-site-text]:hover{outline:2px solid #f2c879!important;outline-offset:3px;filter:brightness(1.08)}`;
    document.head.appendChild(style);
    let resizeStart = null;
    let resizedDuringPointer = false;
    window.addEventListener("pointerdown", (event) => {
      const node = event.target instanceof Element ? event.target.closest("[data-site-editor-key], [data-site-text]") : null;
      if (node) {
        const box = node.closest(".tn-editorial-heading") || node;
        resizeStart = { node, box, width: box.getBoundingClientRect().width };
      }
    }, true);
    window.addEventListener("pointerup", () => {
      if (!resizeStart) return;
      const { node, box, width } = resizeStart;
      resizeStart = null;
      const parentWidth = box.parentElement?.getBoundingClientRect().width || 0;
      const nextWidth = box.getBoundingClientRect().width;
      if (!parentWidth || Math.abs(nextWidth - width) < 6) return;
      resizedDuringPointer = true;
      setTimeout(() => { resizedDuringPointer = false; }, 0);
      const field = node.dataset.siteEditorKey || node.dataset.siteText;
      if (field) window.parent.postMessage({ type: "tn-site-editor-style-change", field, box_width: `${Math.max(5, Math.min(100, Math.round(nextWidth / parentWidth * 100)))}%` }, "*");
    }, true);
    window.addEventListener("click", (event) => {
      if (resizedDuringPointer) {
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();
        resizedDuringPointer = false;
        return;
      }
      const target = event.target instanceof Element
        ? event.target.closest("[data-site-editor-key], [data-site-text]")
        : null;
      if (!target) {
        // En modo edición ningún enlace del sitio debe sacar al operador del
        // editor ni navegar el frame hacia la URL del administrador.
        const link = event.target instanceof Element ? event.target.closest("a") : null;
        if (link) {
          event.preventDefault();
          event.stopPropagation();
          event.stopImmediatePropagation();
        }
        return;
      }
      const field = target.dataset.siteEditorKey || target.dataset.siteText;
      if (!field) return;
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();
      // El editor corre en /app y esta vista en el sitio público. Edge puede
      // resolver el origen canónico con otro protocolo/host durante redirects;
      // el padre valida event.origin y el mensaje no navega el iframe.
      window.parent.postMessage({ type: "tn-site-editor-select", field }, "*");
    }, { capture: true });
  }

  async function loadContent() {
    try {
      let data = {};
      try {
        const defaultsResponse = await fetch(new URL("./assets/data/contenido-sitio.json", location.href), { cache: "no-store" });
        if (defaultsResponse.ok) data = await defaultsResponse.json();
      } catch { /* La API conserva su propio contenido si los defaults no cargan. */ }
      const endpoint = preview && key ? "/api/sitio/contenido" : "/api/sitio/contenido-publico";
      try {
        const response = await fetch(`${API}${endpoint}`, { headers, cache: "no-store" });
        if (response.ok) data = mergeContent(data, await response.json());
      } catch { /* El sitio conserva el contenido público local como respaldo. */ }
      if (!Object.keys(data).length) return;
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
      const hero = data.home?.hero || {};
      const mobileHero = matchMedia("(max-width: 859px)").matches;
      const heroValues = {
        "home.hero.eyebrow": hero.eyebrow,
        "home.hero.title_desktop": mobileHero ? (hero.title_mobile || hero.title_desktop) : hero.title_desktop,
        "home.hero.title_mobile": mobileHero ? (hero.title_mobile || hero.title_desktop) : hero.title_mobile,
        "home.hero.lead": hero.lead,
        "home.hero.cta": hero.cta,
      };
      document.querySelectorAll("[data-site-editor-key]").forEach((node) => {
        if (node.matches(".hero-title")) node.dataset.siteEditorKey = mobileHero ? "home.hero.title_mobile" : "home.hero.title_desktop";
        const value = heroValues[node.dataset.siteEditorKey];
        if (typeof value === "string" && value.trim()) node.textContent = value;
      });
      // La sección editorial de alojamientos estaba escrita directamente en el
      // HTML y no tenía campos CMS; por eso sus títulos no abrían el editor.
      bindEditorialFields(data.home?.unidades_editoriales);
      const unidadGallerySets = ["alpinas", "suite-alta", "suite-baja"];
      const editorialCards = data.home?.unidades_editoriales?.cards;
      (Array.isArray(editorialCards) ? editorialCards : []).forEach((card, index) => {
        const source = document.querySelector(`.tn-photo-source[data-photo-set="${unidadGallerySets[index]}"]`);
        if (!source || !Array.isArray(card?.fotos) || !card.fotos.length) return;
        const fragment = document.createDocumentFragment();
        card.fotos.forEach((photo, photoIndex) => {
          const path = typeof photo === "string" ? photo : photo?.imagen;
          if (typeof path !== "string" || !path.trim()) return;
          const image = document.createElement("img");
          image.src = mediaUrl(path.trim());
          image.alt = typeof photo?.alt === "string" ? photo.alt : `${card.titulo || "Alojamiento"} · vista ${photoIndex + 1}`;
          fragment.appendChild(image);
        });
        source.replaceChildren(fragment);
      });
      const gallery = data.home?.galeria;
      const galleryHeading = document.querySelector("#fotos .tn-editorial-heading h2");
      const galleryLead = document.querySelector("#fotos .tn-editorial-heading p");
      if (galleryHeading) {
        galleryHeading.dataset.siteEditorKey = "home.galeria.titulo";
        if (typeof gallery?.titulo === "string") galleryHeading.textContent = gallery.titulo;
      }
      if (galleryLead) {
        galleryLead.dataset.siteEditorKey = "home.galeria.lead";
        if (typeof gallery?.lead === "string") galleryLead.textContent = gallery.lead;
      }
      if (gallery) {
        const track = document.querySelector("#fotos .tn-photo-grid");
        const fotosPresentables = Array.isArray(gallery?.fotos) ? gallery.fotos.map((photo, originalIndex) => ({ photo, originalIndex })).filter(({ photo }) => !esFotoNoRepresentativa(photo?.imagen)) : [];
        if (track && fotosPresentables.length) {
          const fragment = document.createDocumentFragment();
          fotosPresentables.forEach(({ photo, originalIndex }, index) => {
            if (!photo || typeof photo.imagen !== "string" || !photo.imagen.trim()) return;
            const figure = document.createElement("button");
            figure.type = "button";
            figure.className = "tn-photo-tile";
            figure.dataset.siteEditorKey = `home.galeria.fotos.${originalIndex}.imagen`;
            const image = document.createElement("img");
            image.src = mediaUrl(photo.imagen.trim());
            image.alt = typeof photo.alt === "string" ? photo.alt : "Foto de Terra Natura";
            image.loading = index === 0 ? "eager" : "lazy";
            image.decoding = "async";
            figure.appendChild(image);
            const caption = document.createElement("span");
            caption.textContent = photo.alt || "Ver foto";
            figure.appendChild(caption);
            fragment.appendChild(figure);
          });
          const videoTile = track.querySelector("[data-open-video]");
          if (videoTile) fragment.appendChild(videoTile.cloneNode(true));
          track.replaceChildren(fragment);
          const addPhoto = document.querySelector("#fotos .tn-editorial-heading [data-tn-editor-action]")
            || addEditorAction(document.querySelector("#fotos .tn-editorial-heading"), `home.galeria.fotos.${gallery.fotos.length}.imagen`, "＋ Agregar recuadro de foto");
          if (addPhoto) addPhoto.dataset.siteEditorKey = `home.galeria.fotos.${gallery.fotos.length}.imagen`;
        }
      }
      const configuredSlides = data.home?.hero_slides;
      const slidesPresentables = Array.isArray(configuredSlides) ? configuredSlides.filter((item) => !esFotoNoRepresentativa(item?.imagen)) : [];
      const addCover = document.querySelector('[data-site-editor-key="home.hero_slides.add"]');
      if (addCover) addCover.dataset.siteEditorKey = `home.hero_slides.${configuredSlides?.length || 0}.imagen`;
      if (slidesPresentables.length) {
        const container = document.querySelector(".hero-slides");
        if (container) {
          const fragment = document.createDocumentFragment();
          slidesPresentables.forEach((item, index) => {
            if (typeof item?.imagen !== "string" || !item.imagen.trim()) return;
            const slide = document.createElement("span");
            slide.className = "hero-slide" + (index === 0 ? " is-active" : "");
            slide.dataset.siteEditorKey = `home.hero_slides.${index}.imagen`;
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
            image.dataset.siteEditorKey = `unidades.${unit.id}.foto_portada`;
            image.src = mediaUrl(typeof unit.foto_portada === "string" ? unit.foto_portada : "");
            image.alt = unit.nombre;
            image.loading = "lazy";
            image.decoding = "async";
            imageLink.appendChild(image);
            card.appendChild(imageLink);
            const heading = document.createElement("h3");
            const titleLink = document.createElement("a");
            titleLink.dataset.siteEditorKey = `unidades.${unit.id}.nombre`;
            titleLink.href = href;
            titleLink.textContent = unit.nombre;
            heading.appendChild(titleLink);
            card.appendChild(heading);
            const description = document.createElement("p");
            description.dataset.siteEditorKey = `unidades.${unit.id}.descripcion`;
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
              image.dataset.siteEditorKey = `home.atracciones.${place.id}.foto`;
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
                image.dataset.siteEditorKey = `home.atracciones.${place.id}.foto`;
                image.src = mediaUrl(src);
                image.alt = place.titulo;
                image.loading = "lazy";
                image.decoding = "async";
                photos.appendChild(image);
              });
              card.appendChild(photos);
            }
            const title = document.createElement("h3");
            title.dataset.siteEditorKey = `home.atracciones.${place.id}.titulo`;
            title.textContent = place.titulo;
            card.appendChild(title);
            const description = document.createElement("p");
            description.dataset.siteEditorKey = `home.atracciones.${place.id}.descripcion`;
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
          faqs.forEach((item, index) => {
            const details = document.createElement("details");
            details.className = "faq-item";
            const question = document.createElement("summary");
            question.dataset.siteEditorKey = `home.preguntas_frecuentes.${index}.pregunta`;
            question.textContent = item.pregunta;
            const answer = document.createElement("p");
            answer.dataset.siteEditorKey = `home.preguntas_frecuentes.${index}.respuesta`;
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
          data.home.resenas.forEach((item, index) => {
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
            title.dataset.siteEditorKey = `home.resenas.${index}.titulo`;
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
            quote.dataset.siteEditorKey = `home.resenas.${index}.texto`;
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
      const videoBackdrop = document.querySelector("[data-site-hero-video-backdrop]");
      if (video) {
        const mobile = matchMedia("(max-width: 859px)").matches;
        const src = mobile ? hero.video_mobile : hero.video_desktop;
        if (src) {
          video.poster = mediaUrl(hero.video_poster || "./media/galeria/02-piscina.webp");
          video.src = mediaUrl(src);
          video.hidden = false;
          if (videoBackdrop && mobile) {
            videoBackdrop.src = mediaUrl(src);
            videoBackdrop.hidden = false;
            videoBackdrop.play().catch(() => {});
          }
          const slides = document.querySelector(".hero-slides");
          if (slides) slides.hidden = true;
          if (matchMedia("(prefers-reduced-motion: reduce)").matches || navigator.connection?.saveData) {
            video.pause();
            videoBackdrop?.pause();
          }
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
      const galleryVideo = data.home?.video_galeria;
      const dialogVideo = document.querySelector("#tn-video-dialog video");
      if (dialogVideo && typeof galleryVideo === "string") {
        if (editorPreview) dialogVideo.dataset.siteEditorKey = "home.video_galeria";
        const source = dialogVideo.querySelector("source");
        if (source && galleryVideo.trim()) {
          source.src = mediaUrl(galleryVideo.trim());
          dialogVideo.load();
        }
      }
      const guideVideo = data.home?.video_guia;
      const guideElement = document.querySelector(".tn-guide-film__video");
      if (guideElement && typeof guideVideo === "string") {
        if (editorPreview) guideElement.dataset.siteEditorKey = "home.video_guia";
        const source = guideElement.querySelector("source");
        if (source && guideVideo.trim()) {
          source.src = mediaUrl(guideVideo.trim());
          guideElement.load();
        }
      }
      const editorStyles = data.home?.editor_styles || {};
      Object.entries(editorStyles).forEach(([field, style]) => {
        if (!style || typeof style !== "object") return;
        document.querySelectorAll("[data-site-editor-key], [data-site-text]").forEach((node) => {
          const nodeField = node.dataset.siteEditorKey || node.dataset.siteText;
          if (nodeField !== field) return;
          if (["left", "center", "right", "justify"].includes(style.align)) node.style.textAlign = style.align;
          if (typeof style.font === "string" && style.font.length < 100) node.style.fontFamily = style.font;
          if (/^\d{1,3}px$/.test(style.font_size || "")) node.style.fontSize = style.font_size;
          if (["400", "500", "600", "700", "800", "900"].includes(style.font_weight)) node.style.fontWeight = style.font_weight;
          if (["normal", "italic"].includes(style.font_style)) node.style.fontStyle = style.font_style;
          const box = node.closest(".tn-editorial-heading") || node;
          if (/^(?:[5-9]|[1-9]\d|100)%$/.test(style.box_width || "")) {
            box.style.width = style.box_width;
            box.style.maxWidth = "100%";
          }
          if (["left", "center", "right"].includes(style.box_align)) {
            box.style.marginLeft = style.box_align === "right" || style.box_align === "center" ? "auto" : "0";
            box.style.marginRight = style.box_align === "left" || style.box_align === "center" ? "auto" : "0";
            box.style.display = "block";
          }
        });
      });
      document.documentElement.dataset.siteContentLoaded = "true";
      if (preview && !key) document.documentElement.dataset.sitePreviewUnavailable = "true";
    } catch { /* El HTML local mantiene la versión de respaldo. */ }
  }
  loadContent();
})();
