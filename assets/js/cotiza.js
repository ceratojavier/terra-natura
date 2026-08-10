(function () {
  const WA_BASE = "https://wa.me/5493541571190";
  const BOOKING_URL =
    "https://www.booking.com/hotel/ar/cabanas-alpinas-terra-natura-bialet-masse.es.html";

  const form = document.getElementById("form-reserva");
  const unidad = document.getElementById("reserva-unidad");
  const checkIn = document.getElementById("reserva-in");
  const checkOut = document.getElementById("reserva-out");
  const personas = document.getElementById("reserva-personas");
  const canal = document.getElementById("reserva-canal");
  const nota = document.getElementById("reserva-nota");
  const nombre = document.getElementById("reserva-nombre");
  const email = document.getElementById("reserva-email");
  const resultado = document.getElementById("reserva-resultado");
  const acciones = document.getElementById("reserva-acciones");
  const estadoApi = document.getElementById("reserva-api-estado");

  if (!form || !unidad || !checkIn || !checkOut || !personas || !resultado || !acciones) {
    return;
  }

  const urlParams = new URLSearchParams(location.search);
  const unidadParam = urlParams.get("unidad");
  const checkInParam = urlParams.get("checkin") || urlParams.get("check_in");
  const checkOutParam = urlParams.get("checkout") || urlParams.get("check_out");
  const personasParam = urlParams.get("personas");
  const autoCotizar = urlParams.get("cotizar") === "1";
  if (unidadParam) {
    try {
      unidad.value = unidadParam;
    } catch (_) {}
  }
  if (checkInParam && checkIn) checkIn.value = checkInParam;
  if (checkOutParam && checkOut) checkOut.value = checkOutParam;
  if (personasParam && personas) personas.value = personasParam;

  const API_FALLBACK = "https://terra-natura-api.onrender.com";

  let siteConfig = { apiBase: API_FALLBACK, bookingUrl: BOOKING_URL, whatsapp: "5493541571190" };
  let motorConfig = null;
  let tarifasCache = null;
  let lastCotizacion = null;
  let mpDisponible = false;
  let simuladorActivo = false;

  function ymd(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  }

  function parse(s) {
    const p = s.split("-").map(Number);
    return new Date(p[0], p[1] - 1, p[2]);
  }

  function add(d, n) {
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

  function apiBase() {
    const b = (siteConfig.apiBase || "").trim().replace(/\/$/, "");
    if (b) return b;
    if (
      location.hostname === "alpinasterranatura.com.ar" ||
      location.hostname === "www.alpinasterranatura.com.ar"
    ) {
      return API_FALLBACK;
    }
    if (location.protocol.startsWith("http") && !location.hostname.includes("github.io")) {
      return location.origin;
    }
    return "";
  }

  async function apiFetch(path, options) {
    const base = apiBase();
    if (!base) return null;
    const url = `${base}${path}`;
    const res = await fetch(url, {
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

  function setApiEstado() {
    if (estadoApi) estadoApi.hidden = true;
  }

  function temporadaFactor(inDate) {
    const m = inDate.getMonth() + 1;
    if (m === 1 || m === 2 || m === 7) return 1.22;
    if (m === 3 || m === 4 || m === 12) return 1.1;
    return 1;
  }

  function estimadoLocal(unitId, noches, inDate) {
    const base = {
      "alpina-1": 120000,
      "alpina-2": 120000,
      "alpina-3": 120000,
      "suite-4": 90000,
      "suite-5": 90000,
    };
    const b = base[unitId] || 110000;
    const total = Math.round(b * temporadaFactor(inDate) * noches);
    return { total, senia: Math.round(total * 0.5), origen: "estimado_local" };
  }

  function cotizarDesdeCache(unitId, checkInStr, checkOutStr) {
    if (!tarifasCache || !tarifasCache.precio_noche_por_unidad) return null;
    const porUnidad = tarifasCache.precio_noche_por_unidad[unitId];
    if (!porUnidad) return null;
    const ci = parse(checkInStr);
    const co = parse(checkOutStr);
    let total = 0;
    let noches = 0;
    const cur = new Date(ci.getTime());
    while (cur < co) {
      const key = ymd(cur);
      const p = porUnidad[key];
      if (p == null) return null;
      total += Number(p);
      noches += 1;
      cur.setDate(cur.getDate() + 1);
    }
    if (noches <= 0) return null;
    total = Math.round(total);
    return {
      total,
      senia: Math.round(total * 0.5),
      origen: "motor_cache",
      noches,
    };
  }

  async function cargarConfig() {
    try {
      const sc = await fetch("./assets/data/site-config.json?v=2");
      if (sc.ok) siteConfig = { ...siteConfig, ...(await sc.json()) };
    } catch (_) {}
    try {
      const tc = await fetch("./assets/data/tarifas-cotizador-cache.json?v=2");
      if (tc.ok) tarifasCache = await tc.json();
    } catch (_) {}

    const base = apiBase();
    setApiEstado();
    if (!base) return;

    try {
      motorConfig = await apiFetch("/api/public/motor-reserva");
      if (motorConfig && motorConfig.canales && motorConfig.canales.booking_url) {
        siteConfig.bookingUrl = motorConfig.canales.booking_url;
      }
      if (motorConfig && motorConfig.pagos) {
        mpDisponible = !!motorConfig.pagos.mercadopago_activo;
        simuladorActivo = !!motorConfig.pagos.simulador_activo;
      }
      if (motorConfig && Array.isArray(motorConfig.unidades) && motorConfig.unidades.length) {
        unidad.innerHTML = "";
        motorConfig.unidades.forEach(function (u) {
          const opt = document.createElement("option");
          opt.value = u.id;
          opt.textContent = u.nombre || u.id;
          unidad.appendChild(opt);
        });
      }
    } catch (_) {}
  }

  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  checkIn.min = ymd(hoy);
  checkOut.min = ymd(add(hoy, 1));
  checkIn.value = ymd(add(hoy, 14));
  checkOut.value = ymd(add(hoy, 17));

  checkIn.addEventListener("change", function () {
    const ci = parse(checkIn.value);
    if (Number.isNaN(ci.getTime())) return;
    const co = parse(checkOut.value);
    if (Number.isNaN(co.getTime()) || co <= ci) checkOut.value = ymd(add(ci, 2));
    checkOut.min = ymd(add(ci, 1));
  });

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    acciones.innerHTML = "";
    lastCotizacion = null;

    const ci = parse(checkIn.value);
    const co = parse(checkOut.value);
    const noches = Math.round((co.getTime() - ci.getTime()) / 86400000);
    if (!Number.isFinite(noches) || noches <= 0) {
      resultado.hidden = false;
      resultado.className = "result err";
      resultado.textContent = "Revisá fechas: el check-out debe ser posterior al check-in.";
      return;
    }

    const unitId = unidad.value;
    const unitLabel = unidad.options[unidad.selectedIndex]?.textContent || unitId;
    const personasNum = Number(personas.value || 2);
    let total = 0;
    let senia = 0;
    let disponible = null;
    let fuente = "estimado_local";
    let reservaId = null;

    resultado.hidden = false;
    resultado.className = "result";
    resultado.textContent = "Estamos consultando disponibilidad y precio…";

    const base = apiBase();
    if (base) {
      try {
        const data = await apiFetch("/api/cotizar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            unidad_id: unitId,
            check_in: checkIn.value,
            check_out: checkOut.value,
            promo: "ninguna",
            aplicar_precio_efectivo: false,
          }),
        });
        disponible = data.disponible;
        const cot = data.cotizacion || {};
        total = Number(cot.total) || 0;
        senia = Math.round(total * ((motorConfig && motorConfig.reglas && motorConfig.reglas.sena_pct) || 50) / 100);
        fuente = "pms";
        lastCotizacion = { total, senia, disponible, cot };
      } catch (err) {
        const cache = cotizarDesdeCache(unitId, checkIn.value, checkOut.value);
        if (cache) {
          total = cache.total;
          senia = cache.senia;
          fuente = cache.origen;
        } else {
          const loc = estimadoLocal(unitId, noches, ci);
          total = loc.total;
          senia = loc.senia;
          fuente = "estimado_local";
        }
      }
    } else {
      const cache = cotizarDesdeCache(unitId, checkIn.value, checkOut.value);
      if (cache) {
        total = cache.total;
        senia = cache.senia;
        fuente = cache.origen;
      } else {
        const loc = estimadoLocal(unitId, noches, ci);
        total = loc.total;
        senia = loc.senia;
      }
    }

    let html = "";
    if (disponible === false) {
      resultado.className = "result warn";
      html =
        `<strong>Sin disponibilidad</strong> en el calendario del complejo (incluye reservas Booking sincronizadas).<br>` +
        `Probá otras fechas o consultanos por WhatsApp.`;
    } else if (disponible === true) {
      resultado.className = "result ok";
      html =
        `<strong>Hay lugar</strong> para esas fechas.<br>` +
        `Total: <strong>${fmt(total)}</strong> (${noches} noche${noches === 1 ? "" : "s"}) — tarifa del sistema.<br>` +
        `Seña para confirmar (50%): <strong>${fmt(senia)}</strong>.`;
    } else if (fuente === "pms" || fuente === "motor_cache") {
      resultado.className = "result ok";
      const dispTxt =
        disponible === null
          ? "Confirmamos disponibilidad al reservar (calendario en línea en breve)."
          : "";
      html =
        `<strong>Precio del sistema:</strong> ${fmt(total)} por ${noches} noche${noches === 1 ? "" : "s"} ` +
        `(temporada baja / inflación incluida).<br>` +
        `Seña de referencia (50%): <strong>${fmt(senia)}</strong>.<br>` +
        (dispTxt ? `<small>${dispTxt}</small>` : "");
    } else {
      resultado.className = "result";
      html =
        `<strong>Precio orientativo:</strong> ${fmt(total)} por ${noches} noche${noches === 1 ? "" : "s"}.<br>` +
        `Seña de referencia (50%): <strong>${fmt(senia)}</strong>.<br>` +
        `<small>Te confirmamos el monto final al reservar.</small>`;
    }

    resultado.innerHTML = html;

    const quien = nombre && nombre.value.trim() ? nombre.value.trim() : "te escribo";
    const fechasTxt = `del ${checkIn.value} al ${checkOut.value}`;
    let disponibilidadTxt = "¿Me confirmás si hay lugar para esas fechas?";
    if (disponible === true) {
      disponibilidadTxt = "Vi que habría lugar para esas fechas.";
    } else if (disponible === false) {
      disponibilidadTxt = "Para esas fechas no vi lugar libre; ¿tenés otra opción cercana?";
    }
    const precioTxt = total > 0 ? ` En la web me figuró alrededor de ${fmt(total)}.` : "";

    const msg =
      `Hola, ¿cómo están? Soy ${quien}.\n\n` +
      `Estuve mirando Terra Natura y nos gustaría ir ${fechasTxt}, ` +
      `somos ${personasNum} en ${unitLabel}.\n` +
      disponibilidadTxt +
      precioTxt +
      (nota && nota.value ? `\n\nAlgo para tener en cuenta: ${nota.value}` : "") +
      "\n\n¿Me ayudás a coordinar la reserva? Gracias.";

    const wa = document.createElement("a");
    wa.className = "btn btn-primary";
    wa.href = `${WA_BASE}?text=${encodeURIComponent(msg)}`;
    wa.target = "_blank";
    wa.rel = "noopener noreferrer";
    wa.textContent = "Escribirnos por WhatsApp";
    acciones.appendChild(wa);

    const nombreOk = nombre && nombre.value.trim().length >= 2;
    const emailOk = email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim());
    const puedePagarOnline =
      base && disponible === true && nombreOk && emailOk && (mpDisponible || simuladorActivo);

    if (puedePagarOnline) {
      const btnMp = document.createElement("button");
      btnMp.type = "button";
      btnMp.className = "btn btn-primary";
      btnMp.textContent = simuladorActivo && !mpDisponible
        ? "Probar pago online (modo prueba)"
        : "Pagar seña con Mercado Pago";
      btnMp.addEventListener("click", async function () {
        btnMp.disabled = true;
        btnMp.textContent = "Redirigiendo…";
        try {
          const pay = await apiFetch("/api/public/pagar-preferencia", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              unidad_id: unitId,
              check_in: checkIn.value,
              check_out: checkOut.value,
              huesped_nombre: nombre.value.trim(),
              huesped_email: email.value.trim(),
              personas: personasNum,
            }),
          });
          if (pay && pay.init_point) {
            window.location.href = pay.init_point;
            return;
          }
          alert("No pudimos abrir el pago. Escribinos por WhatsApp y te ayudamos.");
        } catch (err) {
          const det =
            err.body && err.body.detail
              ? typeof err.body.detail === "string"
                ? err.body.detail
                : "No se pudo iniciar el pago online."
              : "No se pudo iniciar el pago online. Escribinos por WhatsApp.";
          alert(det);
        }
        btnMp.disabled = false;
        btnMp.textContent = simuladorActivo && !mpDisponible
          ? "Probar pago online (modo prueba)"
          : "Pagar seña con Mercado Pago";
      });
      acciones.insertBefore(btnMp, wa);
    } else if (base && disponible === true && (!nombreOk || !emailOk)) {
      const hint = document.createElement("p");
      hint.className = "muted";
      hint.style.marginTop = "0.5rem";
      hint.textContent = "Completá nombre y email arriba para pagar la seña online.";
      acciones.appendChild(hint);
    }

  });

  cargarConfig();

  // Si llega desde el hero con datos, cotiza automáticamente para dar precio inmediato.
  if (autoCotizar && checkInParam && checkOutParam) {
    setTimeout(function () {
      try {
        form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
      } catch (_) {}
    }, 220);
  }
})();
