(function () {
  const WA_BASE = "https://wa.me/5493541571190";
  const params = new URLSearchParams(location.search);
  const reservaId = params.get("id") || "";
  const codigo = params.get("codigo") || "";
  const resumen = document.getElementById("senia-resumen");
  const bloque = document.getElementById("senia-pago");
  const err = document.getElementById("senia-error");
  const form = document.getElementById("form-comprobante");
  const msg = document.getElementById("senia-msg");
  const plazoEl = document.getElementById("senia-plazo");
  const datosBanco = document.getElementById("senia-datos-banco");
  const waBtn = document.getElementById("senia-wa-btn");
  const mpBtn = document.getElementById("senia-mp-btn");
  const mpInfo = document.getElementById("senia-mp-info");
  const transferenciaAlternativa = document.getElementById("transferencia-alternativa");

  const API_FALLBACK = "https://api.alpinasterranatura.com.ar";

  function apiBase() {
    if (location.hostname === "alpinasterranatura.com.ar" || location.hostname === "www.alpinasterranatura.com.ar") {
      return API_FALLBACK;
    }
    if (location.protocol.startsWith("http") && !location.hostname.includes("github.io")) {
      return location.origin;
    }
    return API_FALLBACK;
  }

  function fmt(n) {
    return new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(n);
  }

  function pintarDesdeCache() {
    try {
      const raw = sessionStorage.getItem("tn_reserva_ok");
      if (!raw) return null;
      return JSON.parse(raw);
    } catch (_) {
      return null;
    }
  }

  function renderBanco(cache, data) {
    const dp = cache?.datos_pago || {};
    const senia = cache?.senia || data?.senia_referencia;
    const total = cache?.total || data?.precio_total;
    const titular = dp.titular || cache?.titular || "Cerato Carlos Javier";
    const cuil = dp.cuil || "20-28421347-6";
    const alias = dp.alias || cache?.alias_transferencia || "terra.natura";
    const medio = dp.medio || "Mercado Pago (alias)";
    const concepto = dp.concepto || "Seña + código de reserva";
    const linkMercadoPago = cache?.link_mercadopago || "";
    const modoPago = cache?.modo_pago || "";

    if (mpBtn && linkMercadoPago && ["mercadopago", "simulador"].includes(modoPago)) {
      mpBtn.href = linkMercadoPago;
      mpBtn.hidden = false;
      mpBtn.textContent = modoPago === "simulador" ? "Abrir simulador de pago" : "Pagar la seña con Mercado Pago";
      if (mpInfo) mpInfo.hidden = modoPago === "simulador";
      if (transferenciaAlternativa) transferenciaAlternativa.open = false;
    } else if (transferenciaAlternativa) {
      transferenciaAlternativa.open = true;
    }

    datosBanco.innerHTML =
      `<p>Transferí <strong>${fmt(Number(senia))}</strong> (seña 50 % del total ${fmt(Number(total))}).</p>` +
      `<ul style="line-height:1.6;font-size:0.92rem">` +
      `<li><strong>Titular:</strong> ${titular}</li>` +
      `<li><strong>CUIL:</strong> ${cuil}</li>` +
      `<li><strong>Alias:</strong> ${alias}</li>` +
      `<li><strong>Medio:</strong> ${medio}</li>` +
      `<li><strong>Concepto:</strong> ${concepto} · <strong>${codigo}</strong></li>` +
      `</ul>`;

    if (cache?.texto_plazo && plazoEl) plazoEl.textContent = cache.texto_plazo;
    else if (cache?.plazo_horas && plazoEl) {
      plazoEl.textContent =
        "Transferí la seña del 50 % dentro de las próximas " + cache.plazo_horas + " horas para mantener las fechas bloqueadas.";
    }

    const waText =
      cache?.texto_whatsapp ||
      `Hola, soy cliente web Terra Natura. Adjunto comprobante de seña.\nCódigo: ${codigo}\nReserva: ${reservaId}\nGracias.`;
    if (waBtn) {
      waBtn.href = WA_BASE + "?text=" + encodeURIComponent(waText);
      waBtn.hidden = false;
    }
  }

  if (!reservaId || !codigo) {
    err.hidden = false;
    err.textContent = "Falta el link de la reserva. Volvé a reservar desde la web.";
    return;
  }

  const cache = pintarDesdeCache();

  fetch(`${apiBase()}/api/public/reserva/${encodeURIComponent(reservaId)}/estado`)
    .then((r) => (r.ok ? r.json() : Promise.reject()))
    .then((data) => {
      resumen.hidden = false;
      resumen.innerHTML =
        `<strong>Código ${codigo}</strong><br>` +
        `${data.unidad_nombre || ""} · ${data.check_in} → ${data.check_out}<br>` +
        `Total web ${fmt(data.precio_total)} · Seña ${fmt(data.senia_referencia)}`;
      bloque.hidden = false;
      renderBanco(cache, data);
    })
    .catch(() => {
      bloque.hidden = false;
      renderBanco(cache, null);
      if (resumen) {
        resumen.hidden = false;
        resumen.innerHTML = `<strong>Código ${codigo}</strong><br>Transferí la seña para confirmar tu reserva.`;
      }
    });

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    msg.hidden = true;
    const file = document.getElementById("archivo").files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("codigo", codigo);
    fd.append("archivo", file);
    const btn = form.querySelector("button");
    btn.disabled = true;
    btn.textContent = "Enviando…";
    try {
      const res = await fetch(`${apiBase()}/api/public/reserva/${encodeURIComponent(reservaId)}/comprobante`, {
        method: "POST",
        body: fd,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "No se pudo subir el archivo.");
      }
      msg.hidden = false;
      msg.className = "result ok";
      msg.textContent = data.mensaje || "Listo. Te confirmamos cuando veamos el pago.";
      form.reset();
    } catch (ex) {
      msg.hidden = false;
      msg.className = "result err";
      msg.textContent = ex.message || "Error al subir. Probá por WhatsApp.";
    }
    btn.disabled = false;
    btn.textContent = "Enviar comprobante";
  });
})();
