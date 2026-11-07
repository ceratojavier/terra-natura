(function () {
  const WA_BASE = "https://wa.me/5493541571190";
  const API_PROD = "https://api.alpinasterranatura.com.ar";

  const form = document.getElementById("form-reserva");
  const heroForm = document.getElementById("hero-cotiza");
  if (!form && !heroForm) return;

  const unidad = document.getElementById("reserva-unidad");
  const checkIn = document.getElementById("reserva-in");
  const checkOut = document.getElementById("reserva-out");
  const adultosEl = document.getElementById("reserva-adultos");
  const ninosEl = document.getElementById("reserva-ninos");
  const personas = document.getElementById("reserva-personas");
  const nota = document.getElementById("reserva-nota");
  const nombre = document.getElementById("reserva-nombre");
  const email = document.getElementById("reserva-email");
  const telefono = document.getElementById("reserva-telefono");
  const resultado = document.getElementById("reserva-resultado");
  const acciones = document.getElementById("reserva-acciones");
  const heroResultado = document.getElementById("hero-cotiza-resultado");

  const urlParams = new URLSearchParams(location.search);
  const checkInParam = urlParams.get("checkin") || urlParams.get("check_in");
  const checkOutParam = urlParams.get("checkout") || urlParams.get("check_out");
  const adultosParam = urlParams.get("adultos");
  const ninosParam = urlParams.get("ninos");
  const personasParam = urlParams.get("personas");
  const grupoParam = urlParams.get("grupo") || urlParams.get("unidad");
  const nombreParam = urlParams.get("nombre");
  const autoCotizar = urlParams.get("cotizar") === "1";

  const GRUPOS_SELECT = [
    { value: "todas", label: "Ver las 3 opciones de cabaña" },
    { value: "grupo-alpinas", label: "Cabañas Alpinas" },
    { value: "suite-4", label: "Cabaña Suite planta baja" },
    { value: "suite-5", label: "Cabaña Suite planta alta" },
  ];

  const DEFAULT_FOTOS = {
    "grupo-alpinas": [
      "media/galeria/09-alpina-frente-pileta.jpg",
      "media/galeria/05-alpina-living.jpg",
      "media/unidades/alpina-1/03.jpg",
    ],
    "suite-4": ["media/unidades/suite-4/01.jpg", "media/unidades/suite-4/04.jpg"],
    "suite-5": ["media/unidades/suite-5/01.jpg", "media/unidades/suite-5/05.jpg"],
  };

  let siteConfig = { apiBase: API_PROD, whatsapp: "5493541571190" };
  let motorConfig = null;
  let siteContenido = null;
  let lastContext = null;
  let formularioReservaAbierto = false;
  let reservaWebCreada = false;

  function registrarAbandonoReserva() {
    if (!formularioReservaAbierto || reservaWebCreada) return;
    formularioReservaAbierto = false;
    if (window.TNMedicion?.track) window.TNMedicion.track("reservation_form_abandon");
  }
  window.addEventListener("pagehide", registrarAbandonoReserva);

  function ymd(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  }

  function parseYmd(s) {
    const p = s.split("-").map(Number);
    return new Date(p[0], p[1] - 1, p[2]);
  }

  function addDays(d, n) {
    const x = new Date(d.getTime());
    x.setDate(x.getDate() + n);
    return x;
  }

  function fmt(n) {
    return new Intl.NumberFormat("es-AR", {
      style: "currency",
      currency: "ARS",
      maximumFractionDigits: 0,
    }).format(n);
  }

  function fmtFechaAr(iso) {
    const p = iso.slice(0, 10).split("-");
    if (p.length !== 3) return iso;
    return `${p[2]}/${p[1]}/${p[0]}`;
  }

  function apiBase() {
    const b = (siteConfig.apiBase || "").trim().replace(/\/$/, "");
    if (b) return b;
    if (location.hostname === "alpinasterranatura.com.ar" || location.hostname === "www.alpinasterranatura.com.ar") {
      return API_PROD;
    }
    if (location.protocol.startsWith("http") && !location.hostname.includes("github.io")) {
      return location.origin;
    }
    return API_PROD;
  }

  async function apiFetch(path, options) {
    const base = apiBase();
    const res = await fetch(`${base}${path}`, {
      ...options,
      headers: { Accept: "application/json", ...(options && options.headers) },
    });
    if (!res.ok) {
      const err = new Error(`HTTP ${res.status}`);
      err.status = res.status;
      try {
        err.body = await res.json();
      } catch (_) {
        err.body = null;
      }
      throw err;
    }
    return res.json();
  }

  function reservaWebCfg() {
    const rw = siteContenido?.reserva_web || {};
    return {
      descuento_pct: Number(rw.descuento_pct) || 10,
      beneficio_badge: rw.beneficio_badge || "🎁 10 % off reservando directo en la web",
      beneficio_extra: rw.beneficio_extra || "",
      grupos: rw.grupos_cotizador || {},
    };
  }

  function heroCfg() {
    return siteContenido?.home?.hero || {};
  }

  function aplicarTextosPortada() {
    const h = heroCfg();
    const lead = document.querySelector(".hero-copy .lead--desktop");
    if (lead && h.lead) lead.textContent = h.lead;
    let ben = document.querySelector(".hero-beneficio-linea");
    if (h.beneficio_destacado) {
      if (!ben && lead) {
        ben = document.createElement("p");
        ben.className = "hero-beneficio-linea";
        lead.after(ben);
      }
      if (ben) ben.innerHTML = "<strong>" + h.beneficio_destacado + "</strong>";
    }
  }

  function poblarSelectGrupos(selectEl) {
    if (!selectEl) return;
    // Formularios compactos: el grupo puede ser un input oculto.
    if (selectEl.tagName !== "SELECT") {
      if (grupoParam) selectEl.value = grupoParam.startsWith("alpina") ? "grupo-alpinas" : grupoParam;
      return;
    }
    const prev = selectEl.value;
    selectEl.innerHTML = "";
    GRUPOS_SELECT.forEach(function (g) {
      const opt = document.createElement("option");
      opt.value = g.value;
      opt.textContent = g.label;
      selectEl.appendChild(opt);
    });
    if (prev && [...selectEl.options].some((o) => o.value === prev)) selectEl.value = prev;
    else if (grupoParam && [...selectEl.options].some((o) => o.value === grupoParam)) {
      selectEl.value = grupoParam;
    } else if (grupoParam && grupoParam.startsWith("alpina")) {
      selectEl.value = "grupo-alpinas";
    } else if (grupoParam === "suite-4" || grupoParam === "suite-5") {
      selectEl.value = grupoParam;
    }
  }

  function leerAdultosNinos(fromHero) {
    if (fromHero && heroForm) {
      const a = Number(heroForm.querySelector('[name="adultos"]')?.value || 2);
      const n = Number(heroForm.querySelector('[name="ninos"]')?.value || 0);
      return { adultos: Math.max(1, a), ninos: Math.max(0, n) };
    }
    const a = Number(adultosEl?.value || personas?.value || 2);
    const n = Number(ninosEl?.value || 0);
    return { adultos: Math.max(1, a), ninos: Math.max(0, n) };
  }

  function leerGrupo(fromHero) {
    if (fromHero && heroForm) {
      const g = heroForm.querySelector('[name="grupo"]');
      return g ? g.value || "todas" : "todas";
    }
    if (!unidad) return "todas";
    return unidad.value || "todas";
  }

  function leerCodigoPromo(fromHero) {
    const root = fromHero && heroForm ? heroForm : form;
    if (!root) return "";
    const el = root.querySelector('[name="codigo_promo"]');
    return el ? String(el.value || "").trim() : "";
  }

  function leerEdadesMenores(fromHero) {
    const root = fromHero && heroForm ? heroForm : form;
    if (!root) return [];
    const box = root.querySelector("[data-edades-ninos]");
    if (!box) return [];
    return [...box.querySelectorAll("input[type='number']")]
      .map(function (inp) {
        return Number(inp.value);
      })
      .filter(function (n) {
        return Number.isFinite(n) && n >= 0 && n <= 17;
      });
  }

  function syncEdadesNinosContainer(fromHero) {
    const root = fromHero && heroForm ? heroForm : form;
    if (!root) return;
    const ninosInp = fromHero
      ? heroForm.querySelector('[name="ninos"]')
      : ninosEl;
    const box = root.querySelector("[data-edades-ninos]");
    if (!box || !ninosInp) return;
    const n = Math.max(0, Math.min(4, Number(ninosInp.value) || 0));
    box.innerHTML = "";
    if (n === 0) {
      box.hidden = true;
      return;
    }
    box.hidden = false;
    for (let i = 0; i < n; i++) {
      const lab = document.createElement("label");
      lab.className = "hero-field hero-field--half";
      lab.innerHTML =
        "Edad niño " +
        (i + 1) +
        '<input type="number" min="0" max="17" value="8" aria-label="Edad niño ' +
        (i + 1) +
        '" />';
      box.appendChild(lab);
    }
  }

  function payloadAtribucion() {
    if (window.TNAtribucion && typeof window.TNAtribucion.payloadApi === "function") {
      return window.TNAtribucion.payloadApi();
    }
    return null;
  }

  function leerNombre(fromHero) {
    if (fromHero && heroForm) {
      return (heroForm.querySelector('[name="nombre"]')?.value || "").trim();
    }
    return (nombre?.value || "").trim();
  }

  function leerEmail(fromHero) {
    if (fromHero) return "";
    return (email?.value || "").trim();
  }

  function leerTelefono(fromHero) {
    if (fromHero) return "";
    return (telefono?.value || "").trim();
  }

  function configurarFechasMinimas(inEl, outEl) {
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    inEl.min = ymd(hoy);
    outEl.min = ymd(addDays(hoy, 1));
    inEl.addEventListener("change", function () {
      const ci = parseYmd(inEl.value);
      if (Number.isNaN(ci.getTime())) return;
      const co = parseYmd(outEl.value);
      if (Number.isNaN(co.getTime()) || co <= ci) outEl.value = ymd(addDays(ci, 2));
      outEl.min = ymd(addDays(ci, 1));
    });
  }

  function aplicarFechasDesdeUrl(inEl, outEl) {
    if (checkInParam) inEl.value = checkInParam.slice(0, 10);
    if (checkOutParam) outEl.value = checkOutParam.slice(0, 10);
    if (!inEl.value) inEl.value = ymd(addDays(new Date(), 14));
    if (!outEl.value) outEl.value = ymd(addDays(parseYmd(inEl.value), 2));
  }

  async function cargarConfig() {
    try {
      const sc = await fetch("./assets/data/site-config.json?v=4");
      if (sc.ok) siteConfig = { ...siteConfig, ...(await sc.json()) };
    } catch (_) {}

    try {
      const local = await fetch("./assets/data/contenido-sitio.json?v=20261102");
      if (local.ok) siteContenido = await local.json();
    } catch (_) {}

    const base = apiBase();
    if (base) {
      try {
        siteContenido = (await apiFetch("/api/public/contenido-sitio")) || siteContenido;
      } catch (_) {}
      try {
        motorConfig = await apiFetch("/api/public/motor-reserva");
      } catch (_) {}
    }
    aplicarTextosPortada();
  }

  function fotosGrupo(grupoId) {
    const gc = reservaWebCfg().grupos[grupoId] || {};
    const list = (gc.fotos && gc.fotos.length ? gc.fotos : DEFAULT_FOTOS[grupoId]) || [];
    return list.map(function (p) {
      return p.startsWith("http") ? p : "./" + p.replace(/^\.\//, "");
    });
  }

  function featuresGrupo(grupoId) {
    const gc = reservaWebCfg().grupos[grupoId] || {};
    return gc.features || "";
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function carouselHtml(grupoId, cardId) {
    const fotos = fotosGrupo(grupoId);
    if (!fotos.length) return "";
    let imgs = fotos
      .map(function (src, i) {
        return `<img src="${escapeHtml(src)}" alt="" class="${i === 0 ? "is-active" : ""}" loading="lazy" decoding="async" />`;
      })
      .join("");
    if (fotos.length > 1) {
      imgs +=
        `<button type="button" class="cotiza-card-nav cotiza-card-nav--prev" data-carousel="${cardId}" data-dir="-1" aria-label="Foto anterior">‹</button>` +
        `<button type="button" class="cotiza-card-nav cotiza-card-nav--next" data-carousel="${cardId}" data-dir="1" aria-label="Foto siguiente">›</button>`;
    }
    return `<div class="cotiza-card-carousel" data-carousel-id="${cardId}">${imgs}</div>`;
  }

  function initCarousels(root) {
    root.querySelectorAll("[data-carousel]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const id = btn.getAttribute("data-carousel");
        const dir = Number(btn.getAttribute("data-dir"));
        const box = root.querySelector('[data-carousel-id="' + id + '"]');
        if (!box) return;
        const imgs = [...box.querySelectorAll("img")];
        if (imgs.length < 2) return;
        let idx = imgs.findIndex((im) => im.classList.contains("is-active"));
        imgs[idx].classList.remove("is-active");
        idx = (idx + dir + imgs.length) % imgs.length;
        imgs[idx].classList.add("is-active");
      });
    });
  }

  function waMsgOpcion(ctx, o) {
    const fechasTxt = `del ${fmtFechaAr(ctx.check_in)} al ${fmtFechaAr(ctx.check_out)}`;
    return (
      `Hola, soy ${ctx.nombre}. Quiero reservar ${o.etiqueta} en Terra Natura ${fechasTxt}.\n` +
      `Total web: ${fmt(Number(o.cotizacion.total))}. ¿Me confirmás? (TN-WEB)`
    );
  }

  function renderTarjeta(o, ctx, senaPct, cardIdx) {
    const cfg = reservaWebCfg();
    const cardId = "cot-" + cardIdx;
    if (!o.disponible || !o.cotizacion) {
      let det = `<div class="cotiza-card cotiza-card--no"><div class="cotiza-card-body">`;
      det += `<p class="cotiza-card-title">${escapeHtml(o.etiqueta)}</p>`;
      if (o.estadia_minima) {
        const em = o.estadia_minima;
        const minN = em.min_noches || em.min_noches_requeridas || "";
        det += `<p class="cotiza-min-stay-title"><strong>Estadía mínima requerida</strong></p>`;
        det += `<p class="muted">Para estas fechas tenemos una estadía mínima de ${escapeHtml(String(minN))} noches.</p>`;
        if (em.sugerencia) {
          const sug = em.sugerencia;
          det += `<p class="muted">Podés mantener tu ingreso y extender la salida hasta el ${fmtFechaAr(sug.check_out)}.</p>`;
          det += `<p class="cotiza-sug-resumen">Ingreso: ${fmtFechaAr(sug.check_in)} · Salida: ${fmtFechaAr(sug.check_out)} · ${escapeHtml(String(sug.noches || minN))} noches</p>`;
          det += `<div class="cotiza-min-actions">`;
          det += `<button type="button" class="btn btn-primary cotiza-btn-min-aceptar" data-min-in="${sug.check_in}" data-min-out="${sug.check_out}">Aceptar estas fechas</button>`;
          det += `<button type="button" class="btn btn-secondary cotiza-btn-min-otras">Elegir otras fechas</button>`;
          det += `</div>`;
        } else if (o.motivo) {
          det += `<p class="muted">${escapeHtml(o.motivo)}</p>`;
        }
      } else {
        det += `<p class="muted">Sin lugar para esas fechas.</p>`;
        if (o.motivo) det += `<p class="muted">${escapeHtml(o.motivo)}</p>`;
      }
      det += `</div></div>`;
      return det;
    }

    const cot = o.cotizacion;
    const total = Number(cot.total) || 0;
    const lista = Number(cot.total_lista) || total;
    const senia = Math.round(total * (senaPct / 100));
    const descPct = cot.descuento_web_pct || cfg.descuento_pct;

    let html = `<article class="cotiza-card">`;
    html += carouselHtml(o.grupo_id, cardId);
    html += `<div class="cotiza-card-body">`;
    html += `<h3 class="cotiza-card-title">${escapeHtml(o.etiqueta)}</h3>`;
    if (o.capacidad_max) {
      html += `<p class="muted" style="font-size:0.78rem;margin:0 0 0.35rem">Capacidad máxima: ${o.capacidad_max} personas</p>`;
    }
    if (o.unidad_nombre) html += `<p class="muted" style="font-size:0.78rem;margin:0 0 0.35rem">Te asignamos: ${escapeHtml(o.unidad_nombre)}</p>`;
    const feat = featuresGrupo(o.grupo_id);
    if (feat) html += `<p class="cotiza-card-features">${escapeHtml(feat)}</p>`;
    html += `<span class="cotiza-card-beneficio">${escapeHtml(cfg.beneficio_badge)}</span>`;
    if (cfg.beneficio_extra) html += `<p class="muted" style="font-size:0.72rem;margin:0 0 0.35rem">${escapeHtml(cfg.beneficio_extra)}</p>`;
    html += `<div class="cotiza-precios">`;
    if (lista > total) {
      html += `<div class="lista-tachada">Precio lista: ${fmt(lista)}</div>`;
      html += `<div class="total-web">Total web (−${descPct}%): ${fmt(total)}</div>`;
    } else {
      html += `<div class="total-web">Total estadía: ${fmt(total)}</div>`;
    }
    const noches = Number(ctx.noches) || 0;
    if (noches > 0) {
      const nochesTexto = `${noches} noche${noches === 1 ? "" : "s"}`;
      html += `<div class="cotiza-noches-precio"><span>${nochesTexto}</span><span>Precio por noche: <strong>${fmt(total / noches)}</strong></span></div>`;
    }
    html += `<div>Seña 50 %: <strong>${fmt(senia)}</strong></div>`;
    html += `</div>`;
    html += `<div class="cotiza-card-actions">`;
    html += `<button type="button" class="btn-reservar-web" data-reservar="${cardIdx}">Confirmar reserva y ver transferencia</button>`;
    html += `<a class="btn-wa-sec" href="${WA_BASE}?text=${encodeURIComponent(waMsgOpcion(ctx, o))}" target="_blank" rel="noopener noreferrer">Consultar por WhatsApp</a>`;
    html += `</div></div></article>`;
    return html;
  }

  function ensureModal() {
    let m = document.getElementById("cotiza-modal-reserva");
    if (m) return m;
    m = document.createElement("div");
    m.id = "cotiza-modal-reserva";
    m.className = "cotiza-modal";
    m.hidden = true;
    m.innerHTML =
      '<div class="cotiza-modal-backdrop" data-close="1"></div>' +
      '<div class="cotiza-modal-panel" role="dialog" aria-labelledby="cotiza-modal-title">' +
      '<button type="button" class="cotiza-modal-close" data-close="1" aria-label="Cerrar">×</button>' +
      '<h2 id="cotiza-modal-title">Confirmá tu reserva</h2>' +
      '<p class="muted" id="cotiza-modal-sub"></p>' +
      '<form id="cotiza-modal-form">' +
      '<label>Tu nombre<input type="text" name="nombre" required minlength="2" autocomplete="given-name" placeholder="¿Cómo te llamás?" /></label>' +
      '<label>WhatsApp para enviarte la confirmación<input type="tel" name="telefono" required minlength="8" autocomplete="tel" inputmode="tel" /></label>' +
      '<label>Email <span class="muted">(opcional)</span><input type="email" name="email" autocomplete="email" /></label>' +
      '<button type="submit" class="btn-reservar-web">Confirmar reserva y ver datos de transferencia</button>' +
      "</form>" +
      '<p class="cotiza-modal-err" hidden></p>' +
      "</div>";
    document.body.appendChild(m);
    m.querySelectorAll("[data-close]").forEach(function (el) {
      el.addEventListener("click", function () {
        registrarAbandonoReserva();
        m.hidden = true;
      });
    });
    return m;
  }

  function abrirModalReserva(opcion, ctx) {
    formularioReservaAbierto = true;
    reservaWebCreada = false;
    if (window.TNMedicion?.track) window.TNMedicion.track("reservation_form_open");
    const modal = ensureModal();
    const sub = modal.querySelector("#cotiza-modal-sub");
    sub.textContent =
      opcion.etiqueta +
      " · " +
      fmtFechaAr(ctx.check_in) +
      " → " +
      fmtFechaAr(ctx.check_out) +
      " · Total web " +
      fmt(Number(opcion.cotizacion.total));
    const f = modal.querySelector("#cotiza-modal-form");
    f.nombre.value = ctx.nombre || "";
    f.email.value = ctx.email || "";
    f.telefono.value = ctx.telefono || "";
    modal.hidden = false;
    const errEl = modal.querySelector(".cotiza-modal-err");
    errEl.hidden = true;

    f.onsubmit = async function (ev) {
      ev.preventDefault();
      errEl.hidden = true;
      const btn = f.querySelector('button[type="submit"]');
      btn.disabled = true;
      btn.textContent = "Reservando…";
      try {
        const payload = {
          unidad_id: opcion.unidad_id,
          check_in: ctx.check_in,
          check_out: ctx.check_out,
          huesped_nombre: f.nombre.value.trim(),
          huesped_email: f.email.value.trim() || null,
          huesped_telefono: f.telefono.value.trim(),
          personas: ctx.adultos + ctx.ninos,
          adultos: ctx.adultos,
          ninos: ctx.ninos,
          edades_menores: ctx.edades_menores || [],
          codigo_promocional: ctx.codigo_promo || null,
          atribucion: payloadAtribucion(),
        };
        const res = await apiFetch("/api/public/reservar-senia", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        reservaWebCreada = true;
        formularioReservaAbierto = false;
        try {
          sessionStorage.setItem("tn_reserva_ok", JSON.stringify(res));
        } catch (_) {}
        location.href = res.pagina_seña || "./reserva-sena.html?id=" + encodeURIComponent(res.reserva_id) + "&codigo=" + encodeURIComponent(res.codigo);
      } catch (ex) {
        errEl.hidden = false;
        errEl.textContent =
          (ex.body && ex.body.detail) ||
          "No pudimos bloquear esas fechas. Probá de nuevo o escribinos por WhatsApp.";
        btn.disabled = false;
        btn.textContent = "Confirmar reserva y ver datos de transferencia";
      }
    };
  }

  function wireTarjetas(root, ctx, data, fromHero) {
    initCarousels(root);
    const opciones = data.opciones || [];
    root.querySelectorAll("[data-reservar]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const idx = Number(btn.getAttribute("data-reservar"));
        const o = opciones[idx];
        if (!o || !o.disponible) return;
        abrirModalReserva(o, ctx);
      });
    });
    root.querySelectorAll(".cotiza-btn-min-aceptar").forEach(function (btn) {
      btn.addEventListener("click", function () {
        void ejecutarCotizacion({
          fromHero: fromHero,
          forzarFechas: {
            check_in: btn.getAttribute("data-min-in"),
            check_out: btn.getAttribute("data-min-out"),
          },
        });
      });
    });
    root.querySelectorAll(".cotiza-btn-min-otras").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const inEl = fromHero ? heroForm.querySelector('[name="checkin"]') : checkIn;
        if (inEl) inEl.focus();
      });
    });
  }

  async function cotizarOpciones(payload) {
    return apiFetch("/api/public/cotizar-opciones", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  }

  async function ejecutarCotizacion(opts) {
    const fromHero = opts && opts.fromHero;
    const forzarFechas = opts && opts.forzarFechas;

    const inEl = fromHero ? heroForm.querySelector('[name="checkin"]') : checkIn;
    const outEl = fromHero ? heroForm.querySelector('[name="checkout"]') : checkOut;

    let checkInStr = inEl.value;
    let checkOutStr = outEl.value;
    if (forzarFechas?.check_in && forzarFechas?.check_out) {
      checkInStr = forzarFechas.check_in;
      checkOutStr = forzarFechas.check_out;
      inEl.value = checkInStr;
      outEl.value = checkOutStr;
    }

    const ci = parseYmd(checkInStr);
    const co = parseYmd(checkOutStr);
    const noches = Math.round((co.getTime() - ci.getTime()) / 86400000);
    if (!Number.isFinite(noches) || noches <= 0) {
      const err = "Revisá fechas: la salida tiene que ser después del ingreso.";
      if (fromHero && heroResultado) {
        heroResultado.hidden = false;
        heroResultado.className = "hero-cotiza-result err";
        heroResultado.textContent = err;
      } else if (resultado) {
        resultado.hidden = false;
        resultado.className = "result err";
        resultado.textContent = err;
      }
      return;
    }

    const { adultos, ninos } = leerAdultosNinos(fromHero);
    const grupo = leerGrupo(fromHero);
    const grupoFiltro = grupo === "todas" ? null : grupo;
    const quien = leerNombre(fromHero);
    const codigoPromo = leerCodigoPromo(fromHero);
    const edadesMenores = leerEdadesMenores(fromHero);

    const targetResult = fromHero ? heroResultado : resultado;
    const targetAcciones = fromHero ? null : acciones;

    if (targetResult) {
      targetResult.hidden = false;
      targetResult.className = fromHero ? "hero-cotiza-result" : "result";
      targetResult.textContent = "Consultando calendario y tarifas…";
    }
    if (targetAcciones) targetAcciones.innerHTML = "";

    let data;
    try {
      data = await cotizarOpciones({
        check_in: checkInStr,
        check_out: checkOutStr,
        adultos,
        ninos,
        grupo_filtro: grupoFiltro,
        codigo_promocional: codigoPromo || null,
        atribucion: payloadAtribucion(),
      });
    } catch (_) {
      if (targetResult) {
        targetResult.className = (fromHero ? "hero-cotiza-result " : "result ") + "err";
        targetResult.innerHTML =
          "<strong>No pudimos consultar el calendario.</strong> Probá de nuevo en un minuto o escribinos por WhatsApp.";
      }
      return;
    }

    const senaPct = (motorConfig && motorConfig.reglas && motorConfig.reglas.sena_pct) || 50;
    const cfg = reservaWebCfg();
    const ctx = {
      nombre: quien,
      email: leerEmail(fromHero),
      telefono: leerTelefono(fromHero),
      check_in: checkInStr,
      check_out: checkOutStr,
      adultos,
      ninos,
      edades_menores: edadesMenores,
      codigo_promo: codigoPromo,
      noches: data.noches,
    };
    lastContext = ctx;

    let html = "";
    if (data.propuesta_estadia_minima && !data.disponible_alguna) {
      const p = data.propuesta_estadia_minima;
      html += `<div class="cotiza-min-global" role="alert">`;
      html += `<p class="cotiza-min-stay-title"><strong>Estadía mínima requerida</strong></p>`;
      html += `<p class="muted">Para estas fechas tenemos una estadía mínima de ${escapeHtml(String(p.min_noches || ""))} noches.</p>`;
      html += `<p class="muted">Podés mantener tu fecha de ingreso y extender tu salida hasta el ${fmtFechaAr(p.check_out)}.</p>`;
      html += `<p class="cotiza-sug-resumen">Nueva propuesta: ingreso ${fmtFechaAr(p.check_in)} · salida ${fmtFechaAr(p.check_out)} · ${escapeHtml(String(p.noches || p.min_noches))} noches</p>`;
      html += `<p class="muted"><strong>¿Cómo querés continuar?</strong></p>`;
      html += `<div class="cotiza-min-actions">`;
      html += `<button type="button" class="btn btn-primary cotiza-btn-min-aceptar" data-min-in="${p.check_in}" data-min-out="${p.check_out}">Aceptar estas fechas</button>`;
      html += `<button type="button" class="btn btn-secondary cotiza-btn-min-otras">Elegir otras fechas</button>`;
      html += `</div></div>`;
    }
    html += `<p class="cotiza-beneficio-banner">${escapeHtml(cfg.beneficio_badge)}</p>`;

    if (data.disponible_alguna) {
      html += `<p class="cotiza-lead"><strong>Estos son los alojamientos disponibles para tu estadía</strong></p>`;
      (data.opciones || []).forEach(function (o, i) {
        html += renderTarjeta(o, ctx, senaPct, i);
      });
      if (targetResult) targetResult.className = fromHero ? "hero-cotiza-result ok" : "result ok";
    } else {
      html += `<p class="cotiza-lead"><strong>No hay lugar</strong> para esas fechas.</p>`;
      (data.opciones || []).forEach(function (o, i) {
        html += renderTarjeta(o, ctx, senaPct, i);
      });
      if (data.alternativa) {
        const alt = data.alternativa;
        html += `<div class="cotiza-alternativa"><strong>Cerca de lo que pediste:</strong> ${escapeHtml(alt.mensaje || "")}</div>`;
        html += `<button type="button" class="btn btn-secondary cotiza-btn-alt" data-alt-in="${alt.check_in}" data-alt-out="${alt.check_out}">Cotizar ${fmtFechaAr(alt.check_in)} → ${fmtFechaAr(alt.check_out)}</button>`;
      }
      if (targetResult) targetResult.className = fromHero ? "hero-cotiza-result warn" : "result warn";
    }

    if (targetResult) {
      targetResult.innerHTML = html;
      wireTarjetas(targetResult, ctx, data, fromHero);
      targetResult.querySelectorAll(".cotiza-btn-alt").forEach(function (btn) {
        btn.addEventListener("click", function () {
          inEl.value = btn.getAttribute("data-alt-in");
          outEl.value = btn.getAttribute("data-alt-out");
          void ejecutarCotizacion({ fromHero: fromHero });
        });
      });
    }
  }

  if (form && checkIn && checkOut) {
    if (unidad) poblarSelectGrupos(unidad);
    configurarFechasMinimas(checkIn, checkOut);
    aplicarFechasDesdeUrl(checkIn, checkOut);
    if (adultosParam && adultosEl) adultosEl.value = adultosParam;
    if (ninosParam && ninosEl) ninosEl.value = ninosParam;
    if (personasParam && !adultosParam && adultosEl) adultosEl.value = personasParam;
    if (nombreParam && nombre) nombre.value = decodeURIComponent(nombreParam);

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      void ejecutarCotizacion({});
    });
    if (ninosEl) {
      ninosEl.addEventListener("change", function () {
        syncEdadesNinosContainer(false);
      });
      syncEdadesNinosContainer(false);
    }
  }

  if (heroForm) {
    const heroIn = heroForm.querySelector('[name="checkin"]');
    const heroOut = heroForm.querySelector('[name="checkout"]');
    const heroNinos = heroForm.querySelector('[name="ninos"]');
    if (heroNinos) {
      heroNinos.addEventListener("change", function () {
        syncEdadesNinosContainer(true);
      });
      syncEdadesNinosContainer(true);
    }
    const heroGrupo = heroForm.querySelector('[name="grupo"]');
    if (heroGrupo) poblarSelectGrupos(heroGrupo);
    if (heroIn && heroOut) {
      configurarFechasMinimas(heroIn, heroOut);
      aplicarFechasDesdeUrl(heroIn, heroOut);
    }
    const cotBtn = heroForm.querySelector('button[type="submit"]');
    if (cotBtn) cotBtn.classList.add("btn-cotizar-accent");
    heroForm.addEventListener("submit", function (e) {
      e.preventDefault();
      void ejecutarCotizacion({ fromHero: true });
    });
  }

  document.querySelectorAll(".nav-cta-reservar").forEach(function (a) {
    a.setAttribute("href", "./reservar.html");
  });

  cargarConfig().then(function () {
    if (autoCotizar && form && checkIn?.value && checkOut?.value) {
      void ejecutarCotizacion({});
    }
  });
})();
