(function () {
  "use strict";

  const API = "https://api.alpinasterranatura.com.ar";
  const SITE = "https://alpinasterranatura.com.ar";
  const WA = "5493541571190";
  const conversionDefaults = {
    opiniones_titulo: "Lo que dicen nuestros huéspedes",
    opiniones_bajada: "Historias de huéspedes publicadas en el sitio de Terra Natura.",
    opiniones_insignia: "★ 4.9 · Basado en reseñas verificadas",
    lugares_titulo: "Explorá las Sierras · Todo cerca tuyo",
    lugares_bajada: "Una ubicación estratégica para disfrutar el lago, los ríos y los paseos serranos.",
    lugares: [
      { id: "rios", titulo: "Balnearios y Ríos", tiempo: "A 5 min", descripcion: "Acceso rápido a playas del Río Cosquín y el Lago San Roque.", icono: "pool", foto: "media/atracciones/labios-del-indio-v2.png" },
      { id: "miradores", titulo: "Paseos y Miradores", tiempo: "A 8 min", descripcion: "Naturaleza serrana, senderos y puntos panorámicos históricos.", icono: "mountain", foto: "media/atracciones/plaza-federal-atardecer.jpg" },
      { id: "gastronomia", titulo: "Gastronomía Regional", tiempo: "A 5 min", descripcion: "Parrillas, casas de té y opciones gastronómicas locales.", icono: "kitchen", foto: "media/atracciones/peatonal-carlos-paz-v2.png" },
      { id: "ciudades", titulo: "Carlos Paz y Cosquín", tiempo: "A 15 min", descripcion: "Teatros, paseos nocturnos y festivales por ruta.", icono: "sun", foto: "media/atracciones/puente-carlos-paz-noche-v2.png" },
    ],
  };
  const q = new URLSearchParams(location.search);
  const validGroups = new Set(["grupo-alpinas", "suite-4", "suite-5"]);
  let group = validGroups.has(q.get("grupo")) ? q.get("grupo") : "grupo-alpinas";
  let photos = [];
  let photoIndex = 0;
  let toastTimer = 0;

  const units = {
    "grupo-alpinas": {
      title: "Cabaña Alpina",
      tagline: "Un refugio de dos plantas: dormitorio con balcón arriba y living amplio abajo. Ideal para parejas, con espacio para familias con niños.",
      publicType: "alpina",
      whatsappName: "la Cabaña Alpina",
      services: [
        ["stairs", "Dos plantas", "Dormitorio privado arriba y living-comedor en planta baja."],
        ["bed", "Dormitorio matrimonial", "En planta alta, para descansar con privacidad."],
        ["snow", "Aire frío-calor", "En el dormitorio matrimonial."],
        ["fire", "Estufa a gas y panel", "Calor de hogar para las noches serranas."],
        ["mountain", "Balcón con vistas", "Vista a las sierras del Valle de Punilla."],
        ["family", "Living amplio", "Living-comedor con dos camas auxiliares de una plaza."],
        ["kitchen", "Cocina equipada", "Horno y heladera con freezer."],
        ["wifi", "WiFi y Smart TV", "Conectividad y entretenimiento durante la estadía."],
        ["linen", "Baño y ropa blanca", "Baño completo, sábanas y toallas."],
        ["grill", "Pérgola y asador", "Espacio de uso privado para compartir al aire libre."],
        ["pool", "Pileta y parque", "Áreas comunes con juegos para chicos."],
        ["parking", "Estacionamiento", "Lugar individual dentro del complejo."],
      ],
    },
    "suite-4": {
      title: "Suite en planta baja",
      tagline: "Un loft cómodo y práctico, todo en planta baja y con entrada independiente. Ideal para una pareja o pareja con un niño.",
      publicType: "suite",
      whatsappName: "la Suite en planta baja",
      services: [
        ["bed", "Cama matrimonial", "Más una cama de una plaza en el mismo loft."],
        ["stairs", "Todo en planta baja", "Acceso cómodo, sin subir escaleras."],
        ["fan", "Ventilador de techo", "Esta suite no cuenta con aire acondicionado."],
        ["fire", "Estufa a gas", "Un ambiente cálido para los días frescos."],
        ["door", "Entrada independiente", "Acceso propio a la unidad."],
        ["kitchen", "Cocina equipada", "Horno y heladera con freezer."],
        ["wifi", "WiFi y Smart TV", "Conectividad y entretenimiento durante la estadía."],
        ["linen", "Baño y ropa blanca", "Baño completo, sábanas y toallas."],
        ["grill", "Pérgola y asador", "Espacio de uso privado para compartir al aire libre."],
        ["pool", "Pileta y parque", "Áreas comunes con juegos para chicos."],
        ["parking", "Estacionamiento", "Lugar individual dentro del complejo."],
      ],
    },
    "suite-5": {
      title: "Suite en planta alta",
      tagline: "Un loft con aire frío-calor y balcón con vista a las sierras. Ideal para una pareja o pareja con un niño.",
      publicType: "suite",
      whatsappName: "la Suite en planta alta",
      services: [
        ["bed", "Cama matrimonial", "Más una cama de una plaza en el mismo loft."],
        ["snow", "Aire frío-calor", "Confort durante todo el año."],
        ["fire", "Estufa eléctrica", "Un ambiente cálido para disfrutar las noches serranas."],
        ["mountain", "Balcón con vistas", "Un rincón propio para disfrutar las sierras."],
        ["door", "Entrada independiente", "Acceso propio a la unidad."],
        ["kitchen", "Cocina equipada", "Horno y heladera con freezer."],
        ["wifi", "WiFi y Smart TV", "Conectividad y entretenimiento durante la estadía."],
        ["linen", "Baño y ropa blanca", "Baño completo, sábanas y toallas."],
        ["grill", "Pérgola y asador", "Espacio de uso privado para compartir al aire libre."],
        ["pool", "Pileta y parque", "Áreas comunes con juegos para chicos."],
        ["parking", "Estacionamiento", "Lugar individual dentro del complejo."],
      ],
    },
  };

  const icons = {
    bed: '<path d="M3 18v-6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v6M3 14h18M5 10V6a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v4"/><path d="M3 18v2m18-2v2"/>',
    snow: '<path d="M12 2v20M4 6l16 12M20 6 4 18M9 4l3 2 3-2M9 20l3-2 3 2M3 9l3-1 1-3M17 19l1-3 3-1M21 9l-3-1-1-3M7 19l-1-3-3-1"/>',
    mountain: '<path d="m3 19 7-12 4 6 3-4 4 10H3Z"/><path d="m8 19 4-6 4 6M16 5h.01"/>',
    family: '<circle cx="9" cy="7" r="3"/><path d="M3 20v-2a6 6 0 0 1 12 0v2M17 11a3 3 0 1 0 0-6M18 14a5 5 0 0 1 3 4v2"/>',
    kitchen: '<path d="M4 3v8m4-8v8M4 7h4M6 11v10M15 3v18m0-18c3 2 4 5 4 8h-4"/>',
    wifi: '<path d="M5 12.5a11 11 0 0 1 14 0M8 15.5a6.5 6.5 0 0 1 8 0M11 18.5a2 2 0 0 1 2 0M12 21h.01"/>',
    linen: '<path d="M4 5h16v15H4zM4 10h16M8 5v5m8-5v5M7 15h.01M11 15h.01M15 15h.01"/>',
    grill: '<path d="M5 8h14l-2 6H7L5 8ZM7 14l-2 7m12-7 2 7M9 18h6M12 2v3m-5-2 2 3m8-3-2 3"/>',
    pool: '<path d="M3 15c2 0 2-2 4-2s2 2 5 2 3-2 5-2 2 2 4 2M3 20c2 0 2-2 4-2s2 2 5 2 3-2 5-2 2 2 4 2M7 11V5a2 2 0 0 1 4 0v6m0-4h4a2 2 0 0 1 2 2v2"/>',
    parking: '<path d="M5 21V3h8a6 6 0 0 1 0 12H5m4-6h4a2 2 0 0 0 0-4H9"/>',
    stairs: '<path d="M4 20h5v-5h5v-5h6V4"/><path d="M14 4h6v6"/>',
    fan: '<circle cx="12" cy="12" r="2"/><path d="M12 10c-1-5 2-8 5-6 2 2 0 5-3 7M14 12c5-1 8 2 6 5-2 2-5 0-7-3M12 14c1 5-2 8-5 6-2-2 0-5 3-7M10 12c-5 1-8-2-6-5 2-2 5 0 7 3"/>',
    door: '<path d="M5 21V4l14-2v19M5 21h16M15 12h.01"/>',
    pin: '<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>',
    fire: '<path d="M12 22c4.2 0 7-2.9 7-6.7 0-2.5-1.2-4.4-3.5-6.3.2 2-1 3-1.8 3.4C13.7 8.8 11.8 5.8 8.4 3 9 7.5 6 9.3 5.2 12.1 4.2 15.7 6.5 22 12 22Z"/><path d="M12 22c-2.1-1.1-2.8-3.1-1.8-5.1.5-1 1.3-1.6 1.8-2.9 1.5 1.6 2.3 3.1 2.1 4.7-.1 1.5-.8 2.6-2.1 3.3Z"/>',
  };
  const icon = (name) => `<svg viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.sun}</svg>`;
  const title = (id) => units[id]?.title || "Cabaña Alpina";
  const fmtMoney = (amount) => new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(Number(amount || 0));
  const fmtDate = (iso) => {
    const d = new Date(`${iso}T12:00:00`);
    return Number.isNaN(d.getTime()) ? iso : new Intl.DateTimeFormat("es-AR", { day: "numeric", month: "short" }).format(d).replaceAll(".", "");
  };
  const ymdNow = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`; };
  const getVal = (id) => document.getElementById(id).value;
  const isSuite = () => group === "suite-4" || group === "suite-5";
  const setToast = (message) => {
    const el = document.getElementById("toast");
    el.textContent = message;
    el.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("is-visible"), 3500);
  };

  function quoteUrl(checkin, checkout, adults, children, groupId) {
    const params = new URLSearchParams({ checkin, checkout, adultos: String(adults), ninos: String(children), cotizar: "1", grupo: groupId });
    return `${SITE}/reservar.html?${params.toString()}`;
  }

  function updateLinks(total) {
    const ci = getVal("checkin"), co = getVal("checkout");
    const adults = Number(getVal("adults") || 1), children = Number(getVal("children") || 0);
    const url = quoteUrl(ci, co, adults, children, group);
    const text = `Hola, vi la propuesta de ${units[group].whatsappName} en Terra Natura para el ${fmtDate(ci)} al ${fmtDate(co)}. Somos ${adults + children}. ${total ? `La cotización que vi es ${fmtMoney(total)}. ` : ""}¿Me ayudás a avanzar?`;
    const wa = `https://wa.me/${WA}?text=${encodeURIComponent(text)}`;
    for (const id of ["reserve-link", "final-reserve-link", "sticky-reserve-link"]) document.getElementById(id).href = url;
    document.getElementById("sticky-reserve-link").textContent = total ? "Reservar" : "Ver cotización";
    for (const id of ["whatsapp-link", "header-whatsapp"]) document.getElementById(id).href = wa;
    const next = new URL(location.href);
    next.search = new URLSearchParams({ checkin: ci, checkout: co, adultos: String(adults), ninos: String(children), grupo: group }).toString();
    history.replaceState(null, "", next);
  }

  function paintStay() {
    const ci = getVal("checkin"), co = getVal("checkout");
    const adults = Math.max(1, Number(getVal("adults") || 1)), children = Math.max(0, Number(getVal("children") || 0));
    const nights = Math.max(0, Math.round((new Date(`${co}T12:00:00`) - new Date(`${ci}T12:00:00`)) / 86400000));
    const people = adults + children;
    const pax = `${people} ${people === 1 ? "persona" : "personas"}${children ? ` · ${adults} adultos y ${children} ${children === 1 ? "niño" : "niños"}` : ""}`;
    document.getElementById("stay-summary").innerHTML = [
      `<span class="tn-stay-chip">${icon("sun")}${fmtDate(ci)} → ${fmtDate(co)}</span>`,
      `<span class="tn-stay-chip">${icon("bed")}${nights} ${nights === 1 ? "noche" : "noches"}</span>`,
      `<span class="tn-stay-chip">${icon("family")}${pax}</span>`,
    ].join("");
    document.getElementById("price-nights").textContent = `${nights} ${nights === 1 ? "noche" : "noches"} · ${fmtDate(ci)} al ${fmtDate(co)}`;
    document.getElementById("price-night").textContent = people > 0 ? `${pax}` : "";
    document.getElementById("sticky-stay").textContent = `${nights} ${nights === 1 ? "noche" : "noches"} · ${pax}`;
    updateLinks(null);
  }

  function configureUnit() {
    const item = units[group];
    document.getElementById("hero-title").textContent = group === "grupo-alpinas" ? "Tu cabaña alpina en Terra Natura" : `Tu ${item.title.toLowerCase()} en Terra Natura`;
    document.getElementById("offer-title").textContent = item.title;
    document.getElementById("offer-label").textContent = "Tu propuesta personalizada · Terra Natura";
    document.getElementById("offer-tagline").textContent = item.tagline;
    document.getElementById("services-title").textContent = `Todo lo que incluye ${item.title}`;
    document.getElementById("final-title").textContent = `¿Te imaginás en ${item.title}?`;
    document.getElementById("service-grid").innerHTML = item.services.map(([symbol, name, desc]) => `<article class="tn-service"><span class="tn-service__icon">${icon(symbol)}</span><strong>${name}</strong><p>${desc}</p></article>`).join("");
    const whats = document.getElementById("whatsapp-link");
    whats.href = `https://wa.me/${WA}`;
  }

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);

  function renderConversionContent(content) {
    const home = content?.home || {};
    const cfg = { ...conversionDefaults, ...(home.propuesta_conversion || {}) };
    const setText = (id, value) => { const element = document.getElementById(id); if (element && value) element.textContent = value; };
    setText("reviews-title", cfg.opiniones_titulo);
    setText("reviews-subtitle", cfg.opiniones_bajada);
    setText("reviews-badge", cfg.opiniones_insignia);
    setText("nearby-title", cfg.lugares_titulo);
    setText("nearby-subtitle", cfg.lugares_bajada);

    const places = Array.isArray(cfg.lugares) ? conversionDefaults.lugares.map((base) => ({ ...base, ...(cfg.lugares.find((place) => place?.id === base.id) || {}) })) : conversionDefaults.lugares;
    document.getElementById("nearby-grid").innerHTML = places.map((place) => {
      const symbol = icons[place.icono] ? place.icono : "pin";
      const imagePath = String(place.foto || "").trim();
      const imageUrl = /^https?:\/\//i.test(imagePath) ? imagePath : `./${imagePath.replace(/^\.?\//, "")}`;
      return `<article class="tn-nearby-card">${imagePath ? `<img class="tn-nearby-card__photo" src="${escapeHtml(imageUrl)}" alt="${escapeHtml(place.titulo)}" loading="lazy" decoding="async" onerror="this.hidden=true" />` : `<div class="tn-nearby-card__photo-placeholder">${icon(symbol)}</div>`}<div class="tn-nearby-card__body"><span class="tn-nearby-card__time">${escapeHtml(place.tiempo || "")}</span><h3>${escapeHtml(place.titulo)}</h3><p>${escapeHtml(place.descripcion)}</p></div></article>`;
    }).join("");

    const reviews = Array.isArray(home.resenas) ? home.resenas.filter((review) => review && typeof review.texto === "string" && review.texto.trim()).slice(0, 6) : [];
    const grid = document.getElementById("reviews-grid");
    if (!reviews.length) {
      grid.innerHTML = '<p class="tn-reviews__empty">Las opiniones de huéspedes se mostrarán aquí cuando estén cargadas en el editor del sitio.</p>';
      return;
    }
    grid.innerHTML = reviews.map((review) => {
      const score = Number(String(review.puntaje || "").replace(",", "."));
      const stars = Number.isFinite(score) && score > 0 ? Math.min(5, Math.max(1, Math.round(score > 5 ? score / 2 : score))) : 5;
      const trip = Array.isArray(review.etiquetas) ? review.etiquetas.find((tag) => typeof tag === "string" && tag.trim()) : "";
      const guest = review.nombre || "Huésped verificado";
      const provenance = [trip, review.pie || review.fuente].filter(Boolean).join(" · ");
      return `<article class="tn-review-card"><div class="tn-review-card__stars" aria-label="${stars} estrellas">${"★".repeat(stars)}</div>${review.titulo ? `<h3>${escapeHtml(review.titulo)}</h3>` : ""}<blockquote>“${escapeHtml(review.texto)}”</blockquote><footer><strong>${escapeHtml(guest)}</strong><span>${escapeHtml(provenance)}</span></footer></article>`;
    }).join("");
  }

  async function loadConversionContent() {
    let content;
    try {
      const response = await fetch(`${API}/api/public/contenido-sitio`, { headers: { Accept: "application/json" }, cache: "no-store" });
      if (!response.ok) throw new Error("CMS");
      content = await response.json();
    } catch (_) {
      try { content = await fetch("./assets/data/contenido-sitio.json", { cache: "no-store" }).then((response) => response.ok ? response.json() : null); } catch (_) { content = null; }
    }
    renderConversionContent(content || {});
  }

  function positionFor(photo) {
    const p = photo?.presentacion || {};
    const mobile = matchMedia("(max-width: 720px)").matches;
    const x = mobile ? (p.posicion_celular_x ?? 50) : (p.posicion_pc_x ?? 50);
    const oldY = mobile ? p.posicion_celular : p.posicion_pc;
    const y = mobile ? (p.posicion_celular_y ?? oldY ?? 50) : (p.posicion_pc_y ?? oldY ?? 50);
    const zoom = mobile ? (p.zoom_celular ?? 100) : (p.zoom_pc ?? 100);
    document.getElementById("main-photo")?.style.setProperty("--photo-zoom", String(Math.max(50, Math.min(160, Number(zoom) || 100)) / 100));
    document.getElementById("main-photo")?.style.setProperty("--photo-origin", `${x}% ${y}%`);
    return `${x}% ${y}%`;
  }

  function showPhoto(index) {
    if (!photos.length) return;
    photoIndex = (index + photos.length) % photos.length;
    const photo = photos[photoIndex];
    const img = document.getElementById("main-photo");
    img.src = photo.url;
    img.alt = `${units[group].title}, foto ${photoIndex + 1} de ${photos.length}`;
    img.style.objectPosition = positionFor(photo);
    document.getElementById("photo-backdrop").src = photo.url;
    document.getElementById("photo-counter").textContent = `${String(photoIndex + 1).padStart(2, "0")} / ${String(photos.length).padStart(2, "0")}`;
    Array.from(document.getElementById("photo-thumbs").children).forEach((el, i) => el.setAttribute("aria-current", String(i === photoIndex)));
    if (document.getElementById("photo-lightbox").open) syncLightboxPhoto();
  }

  function syncLightboxPhoto() {
    if (!photos.length) return;
    const photo = photos[photoIndex];
    const image = document.getElementById("lightbox-photo");
    image.src = photo.url;
    image.alt = `${units[group].title}, foto ${photoIndex + 1} de ${photos.length}`;
    image.style.objectPosition = positionFor(photo);
    document.getElementById("lightbox-caption").textContent = `${units[group].title} · Terra Natura · Bialet Massé`;
    document.getElementById("lightbox-counter").textContent = `${String(photoIndex + 1).padStart(2, "0")} / ${String(photos.length).padStart(2, "0")}`;
  }

  function openLightbox() {
    if (!photos.length) return;
    const lightbox = document.getElementById("photo-lightbox");
    syncLightboxPhoto();
    if (!lightbox.open) lightbox.showModal();
    document.documentElement.style.overflow = "hidden";
  }

  function closeLightbox() {
    const lightbox = document.getElementById("photo-lightbox");
    if (lightbox.open) lightbox.close();
    document.documentElement.style.overflow = "";
  }

  function renderPhotos(data) {
    const defaultPhotos = group === "grupo-alpinas"
      ? ["media/galeria/09-alpina-frente-pileta.jpg", "media/galeria/05-alpina-living.jpg", "media/unidades/alpina-1/03.jpg"]
      : group === "suite-4" ? ["media/unidades/suite-4/01.jpg", "media/unidades/suite-4/04.jpg"] : ["media/unidades/suite-5/01.jpg", "media/unidades/suite-5/05.jpg"];
    photos = (data?.fotos || []).filter((f) => f?.url);
    if (!photos.length) photos = defaultPhotos.map((path) => ({ ruta: path, url: `${SITE}/${path}` }));
    const thumbs = document.getElementById("photo-thumbs");
    thumbs.replaceChildren();
    photos.forEach((photo, index) => {
      const button = document.createElement("button");
      const image = document.createElement("img");
      button.type = "button"; button.className = "tn-gallery__thumb"; button.setAttribute("aria-label", `Ver foto ${index + 1}`); button.setAttribute("aria-current", "false");
      image.src = photo.url; image.alt = ""; image.loading = "lazy"; image.decoding = "async";
      button.appendChild(image); button.addEventListener("click", () => showPhoto(index)); thumbs.appendChild(button);
    });
    document.getElementById("gallery-note").textContent = `${photos.length} fotos seleccionadas para esta opción`;
    showPhoto(0);
  }

  async function loadPhotos() {
    try {
      const data = await fetch(`${API}/api/public/coleccion-consulta/${units[group].publicType}`, { headers: { Accept: "application/json" } }).then((r) => { if (!r.ok) throw new Error("album"); return r.json(); });
      renderPhotos(data);
    } catch (_) { renderPhotos(null); }
  }

  function showPrice(option, nights) {
    const cot = option.cotizacion || {};
    const total = Number(cot.total || 0);
    const list = Number(cot.total_lista || total);
    const discount = Number(cot.descuento_web_pct || 0);
    const deposit = Math.round(total * .5);
    document.getElementById("price-total").textContent = fmtMoney(total);
    document.getElementById("sticky-total").textContent = fmtMoney(total);
    const listEl = document.getElementById("price-list");
    if (list > total && discount > 0) { listEl.hidden = false; listEl.innerHTML = `<del>${fmtMoney(list)}</del> <strong>${discount}% de beneficio reservando online</strong>`; }
    else listEl.hidden = true;
    document.getElementById("price-deposit").textContent = fmtMoney(deposit);
    document.getElementById("price-night").textContent = nights > 0 ? `${fmtMoney(total / nights)} por noche` : "";
    const status = document.getElementById("price-status");
    status.textContent = "Disponibilidad consultada ahora. Se confirma al avanzar con la reserva.";
    document.querySelector(".tn-price-card").classList.remove("is-error");
    updateLinks(total);
  }

  function setBusy(busy) {
    const button = document.getElementById("update-quote");
    button.disabled = busy;
    button.textContent = busy ? "Consultando el calendario…" : "Actualizar disponibilidad y precio";
    document.querySelector(".tn-price-card").classList.toggle("is-updating", busy);
  }

  function offerUrl(groupId) {
    const p = new URLSearchParams({ checkin: getVal("checkin"), checkout: getVal("checkout"), adultos: getVal("adults"), ninos: getVal("children"), grupo: groupId });
    return `${SITE}/propuesta.html?${p.toString()}`;
  }

  async function fetchOptions(groupFilter) {
    const payload = {
      check_in: getVal("checkin"), check_out: getVal("checkout"),
      adultos: Math.max(1, Number(getVal("adults") || 1)), ninos: Math.max(0, Number(getVal("children") || 0)),
      grupo_filtro: groupFilter,
    };
    const response = await fetch(`${API}/api/public/cotizar-opciones`, {
      method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(payload),
    });
    if (!response.ok) {
      let detail = "No pudimos consultar el calendario.";
      try { detail = (await response.json()).detail || detail; } catch (_) {}
      throw new Error(detail);
    }
    return response.json();
  }

  function showAlternatives(options, reason) {
    const section = document.getElementById("alternatives");
    document.getElementById("stay-editor").open = true;
    const usable = (options || []).filter((o) => o.disponible && o.cotizacion && validGroups.has(o.grupo_id));
    const names = { "grupo-alpinas": "Cabaña Alpina", "suite-4": "Suite en planta baja", "suite-5": "Suite en planta alta" };
    section.hidden = false;
    section.innerHTML = `<h3>${usable.length ? "Mirá estas opciones disponibles" : "No encontramos lugar en estas fechas"}</h3><p>${reason || (usable.length ? "Cambiaron las fechas o los pasajeros; estas son las propuestas que sí coinciden." : "Probá otras fechas o escribinos y buscamos una alternativa.")}</p>`;
    usable.forEach((o) => {
      const card = document.createElement("div"); card.className = "tn-alternative-card";
      const info = document.createElement("span"); info.innerHTML = `<strong>${names[o.grupo_id] || o.etiqueta}</strong><br><small>${fmtMoney(o.cotizacion.total)} total</small>`;
      const link = document.createElement("a"); link.href = offerUrl(o.grupo_id); link.textContent = "Ver propuesta →";
      card.append(info, link); section.appendChild(card);
    });
    const price = document.querySelector(".tn-price-card");
    price.classList.add("is-error");
    document.getElementById("price-total").textContent = "—";
    document.getElementById("sticky-total").textContent = "Ver opciones";
    document.getElementById("sticky-reserve-link").href = "#alternatives";
    document.getElementById("sticky-reserve-link").textContent = "Ver opciones";
    document.getElementById("price-list").hidden = true;
    document.getElementById("price-deposit").textContent = "—";
    document.getElementById("price-status").textContent = reason || "La propuesta seleccionada necesita una nueva consulta.";
    section.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  async function refreshQuote({ initial = false } = {}) {
    const ci = getVal("checkin"), co = getVal("checkout");
    if (!ci || !co || co <= ci) {
      if (!initial) setToast("Revisá las fechas: la salida tiene que ser posterior al ingreso.");
      document.getElementById("price-status").textContent = "Completá las fechas para calcular tu estadía.";
      document.getElementById("price-total").textContent = "Elegí tus fechas";
      document.getElementById("sticky-total").textContent = "Elegí tus fechas";
      return;
    }
    setBusy(true);
    document.getElementById("alternatives").hidden = true;
    const nights = Math.round((new Date(`${co}T12:00:00`) - new Date(`${ci}T12:00:00`)) / 86400000);
    paintStay();
    try {
      const selectedData = await fetchOptions(group);
      const selected = (selectedData.opciones || []).find((o) => o.grupo_id === group && o.disponible && o.cotizacion);
      if (selected) {
        showPrice(selected, nights);
        if (!initial) setToast("Listo: actualizamos disponibilidad y tarifa para esta propuesta.");
      } else {
        const allData = await fetchOptions(null);
        const cap = units[group].title;
        const reason = Number(getVal("adults")) + Number(getVal("children")) > (group === "grupo-alpinas" ? 4 : 3)
          ? `${cap} no admite esa cantidad de pasajeros. Estas son las opciones válidas.`
          : "Esta opción no está disponible para esas fechas. Estas son las alternativas con lugar.";
        showAlternatives(allData.opciones || [], reason);
      }
    } catch (error) {
      document.querySelector(".tn-price-card").classList.add("is-error");
      document.getElementById("price-total").textContent = "No disponible";
      document.getElementById("sticky-total").textContent = "Consultar tarifa";
      document.getElementById("price-status").textContent = error instanceof Error ? error.message : "No pudimos consultar el calendario.";
      if (!initial) setToast("No pudimos actualizar la propuesta. Probá otra vez.");
    } finally { setBusy(false); }
  }

  const inputCheckin = document.getElementById("checkin");
  inputCheckin.min = ymdNow();
  inputCheckin.value = q.get("checkin") || q.get("check_in") || "";
  document.getElementById("checkout").value = q.get("checkout") || q.get("check_out") || "";
  document.getElementById("adults").value = String(Math.max(1, Number(q.get("adultos") || 2)));
  document.getElementById("children").value = String(Math.max(0, Number(q.get("ninos") || 0)));

  configureUnit();
  loadConversionContent();
  paintStay();
  loadPhotos();
  document.getElementById("quote-form").addEventListener("submit", (event) => { event.preventDefault(); refreshQuote(); });
  document.getElementById("photo-prev").addEventListener("click", () => showPhoto(photoIndex - 1));
  document.getElementById("photo-next").addEventListener("click", () => showPhoto(photoIndex + 1));
  document.getElementById("lightbox-open").addEventListener("click", openLightbox);
  document.getElementById("main-photo").addEventListener("click", openLightbox);
  document.getElementById("lightbox-close").addEventListener("click", closeLightbox);
  document.getElementById("lightbox-prev").addEventListener("click", () => showPhoto(photoIndex - 1));
  document.getElementById("lightbox-next").addEventListener("click", () => showPhoto(photoIndex + 1));
  document.getElementById("photo-lightbox").addEventListener("click", (event) => { if (event.target === event.currentTarget) closeLightbox(); });
  document.getElementById("photo-lightbox").addEventListener("close", () => { document.documentElement.style.overflow = ""; });
  document.getElementById("photo-lightbox").addEventListener("cancel", () => { document.documentElement.style.overflow = ""; });
  document.addEventListener("keydown", (event) => {
    if (!document.getElementById("photo-lightbox").open) return;
    if (event.key === "ArrowLeft") { event.preventDefault(); showPhoto(photoIndex - 1); }
    if (event.key === "ArrowRight") { event.preventDefault(); showPhoto(photoIndex + 1); }
  });
  let touchX = null;
  document.getElementById("gallery-stage").addEventListener("touchstart", (event) => { touchX = event.changedTouches[0].screenX; }, { passive: true });
  document.getElementById("gallery-stage").addEventListener("touchend", (event) => {
    if (touchX === null) return;
    const delta = event.changedTouches[0].screenX - touchX;
    if (Math.abs(delta) > 45) showPhoto(photoIndex + (delta < 0 ? 1 : -1));
    touchX = null;
  }, { passive: true });
  let lightboxTouchX = null;
  document.getElementById("photo-lightbox").addEventListener("touchstart", (event) => { lightboxTouchX = event.changedTouches[0].screenX; }, { passive: true });
  document.getElementById("photo-lightbox").addEventListener("touchend", (event) => {
    if (lightboxTouchX === null) return;
    const delta = event.changedTouches[0].screenX - lightboxTouchX;
    if (Math.abs(delta) > 45) showPhoto(photoIndex + (delta < 0 ? 1 : -1));
    lightboxTouchX = null;
  }, { passive: true });
  const mobileBookingBar = document.getElementById("mobile-booking-bar");
  const quoteObserver = new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting) mobileBookingBar.dataset.quoteSeen = "true";
    const show = matchMedia("(max-width: 767px)").matches && mobileBookingBar.dataset.quoteSeen === "true" && !entry.isIntersecting;
    mobileBookingBar.classList.toggle("is-visible", show);
    mobileBookingBar.setAttribute("aria-hidden", String(!show));
    mobileBookingBar.inert = !show;
  }, { threshold: .12 });
  quoteObserver.observe(document.getElementById("booking-card"));
  window.addEventListener("resize", () => { const image = photos[photoIndex]; if (image) document.getElementById("main-photo").style.objectPosition = positionFor(image); });

  if (inputCheckin.value && document.getElementById("checkout").value) refreshQuote({ initial: true });
})();
