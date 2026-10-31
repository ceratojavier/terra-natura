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

  let siteConfig = { apiBase: API_PROD, whatsapp: "5493541571190" };
  let motorConfig = null;
  let mpDisponible = false;
  let simuladorActivo = false;
  let lastOpciones = null;

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
    return "";
  }

  async function apiFetch(path, options) {
    const base = apiBase();
    if (!base) return null;
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

  function poblarSelectGrupos(selectEl) {
    if (!selectEl) return;
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
      return heroForm.querySelector('[name="grupo"]')?.value || "todas";
    }
    return unidad?.value || "todas";
  }

  function leerNombre(fromHero) {
    if (fromHero && heroForm) {
      return (heroForm.querySelector('[name="nombre"]')?.value || "").trim();
    }
    return (nombre?.value || "").trim();
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
      const sc = await fetch("./assets/data/site-config.json?v=3");
      if (sc.ok) siteConfig = { ...siteConfig, ...(await sc.json()) };
    } catch (_) {}

    const base = apiBase();
    if (!base) return;
    try {
      motorConfig = await apiFetch("/api/public/motor-reserva");
      if (motorConfig?.pagos) {
        mpDisponible = !!motorConfig.pagos.mercadopago_activo;
        simuladorActivo = !!motorConfig.pagos.simulador_activo;
      }
    } catch (_) {}
  }

  function mensajeWhatsApp(opts) {
    const quien = opts.nombre || "te escribo";
    const fechasTxt = `del ${fmtFechaAr(opts.check_in)} al ${fmtFechaAr(opts.check_out)}`;
    const pax = `${opts.adultos} adulto${opts.adultos === 1 ? "" : "s"}${
      opts.ninos ? ` y ${opts.ninos} niño${opts.ninos === 1 ? "" : "s"}` : ""
    }`;

    let cuerpo =
      `Hola, ¿cómo están? Soy ${quien}.\n\n` +
      `Quiero cotizar en Terra Natura ${fechasTxt}, somos ${pax}.\n\n`;

    if (opts.opciones && opts.opciones.length) {
      cuerpo += "Me interesa:\n";
      opts.opciones.forEach(function (o) {
        if (!o.disponible || !o.cotizacion) return;
        const tot = Number(o.cotizacion.total) || 0;
        cuerpo += `• ${o.etiqueta}: ${fmt(tot)} (${opts.noches} noche${opts.noches === 1 ? "" : "s"})`;
        if (o.unidad_nombre && o.grupo_id === "grupo-alpinas") {
          cuerpo += ` — nos asignarían ${o.unidad_nombre}`;
        }
        cuerpo += "\n";
      });
    }

    cuerpo += "\n¿Me confirmás disponibilidad y cómo seguimos con la reserva? Gracias. (TN-COTIZA)";
    if (opts.nota) cuerpo += `\n\nNota: ${opts.nota}`;
    return cuerpo;
  }

  function renderTarjetaOpcion(o, noches, senaPct) {
    const pct = senaPct || 50;
    if (o.disponible && o.cotizacion) {
      const total = Number(o.cotizacion.total) || 0;
      const senia = Math.round(total * (pct / 100));
      let det = `<strong>${o.etiqueta}</strong> — <span class="ok-inline">Hay lugar</span><br>`;
      if (o.unidad_nombre) {
        det += `<span class="muted">Unidad: ${o.unidad_nombre}</span><br>`;
      }
      if (o.nota) det += `<span class="muted">${o.nota}</span><br>`;
      det += `Total: <strong>${fmt(total)}</strong> (${noches} noche${noches === 1 ? "" : "s"}) · Seña ${pct}%: <strong>${fmt(senia)}</strong>`;
      return `<div class="cotiza-opcion cotiza-opcion--ok">${det}</div>`;
    }
    let det = `<strong>${o.etiqueta}</strong> — <span class="warn-inline">Sin lugar</span>`;
    if (o.motivo) det += `<br><span class="muted">${o.motivo}</span>`;
    if (o.estadia_minima?.sugerencia) {
      const s = o.estadia_minima.sugerencia;
      det += `<br><span class="muted">Mínimo ${o.estadia_minima.min_noches || s.noches} noches: sugerimos ${fmtFechaAr(s.check_in)} → ${fmtFechaAr(s.check_out)}.</span>`;
    }
    return `<div class="cotiza-opcion cotiza-opcion--no">${det}</div>`;
  }

  function botonWhatsApp(msg, container) {
    const wa = document.createElement("a");
    wa.className = "btn btn-primary";
    wa.href = `${WA_BASE}?text=${encodeURIComponent(msg)}`;
    wa.target = "_blank";
    wa.rel = "noopener noreferrer";
    wa.textContent = "Escribirnos por WhatsApp";
    container.appendChild(wa);
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

    const targetResult = fromHero ? heroResultado : resultado;
    const targetAcciones = fromHero ? null : acciones;

    if (targetResult) {
      targetResult.hidden = false;
      targetResult.className = fromHero ? "hero-cotiza-result" : "result";
      targetResult.textContent = "Consultando calendario y tarifas…";
    }
    if (targetAcciones) targetAcciones.innerHTML = "";

    const base = apiBase();
    if (!base) {
      if (targetResult) {
        targetResult.className = (fromHero ? "hero-cotiza-result " : "result ") + "err";
        targetResult.textContent =
          "No pudimos conectar con el calendario. Escribinos por WhatsApp y te cotizamos al toque.";
      }
      return;
    }

    let data;
    try {
      data = await cotizarOpciones({
        check_in: checkInStr,
        check_out: checkOutStr,
        adultos,
        ninos,
        grupo_filtro: grupoFiltro,
      });
    } catch (_) {
      if (targetResult) {
        targetResult.className = (fromHero ? "hero-cotiza-result " : "result ") + "err";
        targetResult.innerHTML =
          "<strong>No pudimos consultar el calendario.</strong> Probá de nuevo en un minuto o escribinos por WhatsApp.";
      }
      return;
    }

    lastOpciones = data;
    const senaPct = (motorConfig && motorConfig.reglas && motorConfig.reglas.sena_pct) || 50;
    const opcionesDisp = (data.opciones || []).filter((o) => o.disponible);
    let html = "";

    if (data.disponible_alguna) {
      html += `<p class="cotiza-lead"><strong>Hay opciones para tus fechas.</strong> Calendario y tarifas del sistema:</p>`;
      (data.opciones || []).forEach(function (o) {
        html += renderTarjetaOpcion(o, data.noches, senaPct);
      });
      if (targetResult) targetResult.className = fromHero ? "hero-cotiza-result ok" : "result ok";
    } else {
      html += `<p class="cotiza-lead"><strong>No hay lugar</strong> para esas fechas en el calendario (reservas y bloqueos incluidos).</p>`;
      (data.opciones || []).forEach(function (o) {
        html += renderTarjetaOpcion(o, data.noches, senaPct);
      });
      if (data.alternativa) {
        const alt = data.alternativa;
        html += `<div class="cotiza-alternativa"><strong>Cerca de lo que pediste:</strong> ${alt.mensaje || ""}</div>`;
        const btnAlt = `data-alt-in="${alt.check_in}" data-alt-out="${alt.check_out}"`;
        html += `<button type="button" class="btn btn-secondary cotiza-btn-alt" ${btnAlt}>Cotizar ${fmtFechaAr(alt.check_in)} → ${fmtFechaAr(alt.check_out)}</button>`;
      }
      if (targetResult) targetResult.className = fromHero ? "hero-cotiza-result warn" : "result warn";
    }

    if (targetResult) targetResult.innerHTML = html;

    const msg = mensajeWhatsApp({
      nombre: quien,
      check_in: checkInStr,
      check_out: checkOutStr,
      adultos,
      ninos,
      noches: data.noches,
      opciones: opcionesDisp.length ? opcionesDisp : data.opciones,
      nota: nota && nota.value ? nota.value.trim() : "",
    });

    if (fromHero && heroResultado) {
      const row = document.createElement("div");
      row.className = "hero-cotiza-acciones";
      botonWhatsApp(msg, row);
      heroResultado.appendChild(row);
      heroResultado.querySelectorAll(".cotiza-btn-alt").forEach(function (btn) {
        btn.addEventListener("click", function () {
          inEl.value = btn.getAttribute("data-alt-in");
          outEl.value = btn.getAttribute("data-alt-out");
          void ejecutarCotizacion({ fromHero: true });
        });
      });
    } else if (targetAcciones) {
      botonWhatsApp(msg, targetAcciones);

      const nombreOk = quien.length >= 2;
      const emailOk = email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim());
      const mejor = opcionesDisp[0];
      if (mejor && nombreOk && emailOk && (mpDisponible || simuladorActivo)) {
        const btnMp = document.createElement("button");
        btnMp.type = "button";
        btnMp.className = "btn btn-primary";
        btnMp.textContent = mpDisponible ? "Pagar seña (Mercado Pago)" : "Probar pago online";
        btnMp.addEventListener("click", async function () {
          btnMp.disabled = true;
          try {
            const pay = await apiFetch("/api/public/pagar-preferencia", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                unidad_id: mejor.unidad_id,
                check_in: checkInStr,
                check_out: checkOutStr,
                huesped_nombre: quien,
                huesped_email: email.value.trim(),
                personas: adultos + ninos,
              }),
            });
            if (pay?.init_point) window.location.href = pay.init_point;
            else alert("No pudimos abrir el pago. Usá WhatsApp.");
          } catch (err) {
            alert("No se pudo iniciar el pago online. Escribinos por WhatsApp.");
          }
          btnMp.disabled = false;
        });
        targetAcciones.insertBefore(btnMp, targetAcciones.firstChild);
      } else if (mejor && !nombreOk) {
        const hint = document.createElement("p");
        hint.className = "muted";
        hint.textContent = "Completá tu nombre arriba para iniciar pago online (email opcional para MP).";
        targetAcciones.appendChild(hint);
      }

      targetResult.querySelectorAll(".cotiza-btn-alt").forEach(function (btn) {
        btn.addEventListener("click", function () {
          checkIn.value = btn.getAttribute("data-alt-in");
          checkOut.value = btn.getAttribute("data-alt-out");
          void ejecutarCotizacion({});
        });
      });
    }
  }

  if (form && checkIn && checkOut && unidad) {
    poblarSelectGrupos(unidad);
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
  }

  if (heroForm) {
    const heroIn = heroForm.querySelector('[name="checkin"]');
    const heroOut = heroForm.querySelector('[name="checkout"]');
    const heroGrupo = heroForm.querySelector('[name="grupo"]');
    if (heroGrupo) poblarSelectGrupos(heroGrupo);
    if (heroIn && heroOut) {
      configurarFechasMinimas(heroIn, heroOut);
      aplicarFechasDesdeUrl(heroIn, heroOut);
    }
    heroForm.addEventListener("submit", function (e) {
      e.preventDefault();
      void ejecutarCotizacion({ fromHero: true });
    });
  }

  cargarConfig().then(function () {
    if (autoCotizar && form && checkIn?.value && checkOut?.value) {
      void ejecutarCotizacion({});
    }
  });
})();
