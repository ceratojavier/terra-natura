(function () {
  const params = new URLSearchParams(location.search);
  const reservaId = params.get("id") || "";
  const codigo = params.get("codigo") || "";
  const resumen = document.getElementById("senia-resumen");
  const bloque = document.getElementById("senia-pago");
  const err = document.getElementById("senia-error");
  const form = document.getElementById("form-comprobante");
  const msg = document.getElementById("senia-msg");

  const API_FALLBACK = "https://api.alpinasterranatura.com.ar";

  function apiBase() {
    if (
      location.hostname === "alpinasterranatura.com.ar" ||
      location.hostname === "www.alpinasterranatura.com.ar"
    ) {
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

  if (!reservaId || !codigo) {
    err.hidden = false;
    err.textContent = "Falta el link de la reserva. Volvé a reservar desde la web.";
    return;
  }

  fetch(`${apiBase()}/api/public/reserva/${encodeURIComponent(reservaId)}/estado`)
    .then((r) => (r.ok ? r.json() : Promise.reject()))
    .then((data) => {
      resumen.hidden = false;
      resumen.innerHTML =
        `<strong>Código ${codigo}</strong><br>` +
        `${data.unidad_nombre || ""} · ${data.check_in} → ${data.check_out}<br>` +
        `Total ${fmt(data.precio_total)} · Seña ${fmt(data.senia_referencia)}`;
      bloque.hidden = false;
      document.getElementById("senia-alias").innerHTML =
        `Transferí <strong>${fmt(data.senia_referencia)}</strong> al alias Mercado Pago ` +
        `<strong>terra.natura</strong> (titular CERATO C. JAVIER).<br>` +
        `En el concepto poné tu código: <strong>${codigo}</strong>.`;
    })
    .catch(() => {
      bloque.hidden = false;
      document.getElementById("senia-alias").textContent =
        "Transferí la seña al alias terra.natura (Mercado Pago) y subí el comprobante abajo.";
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
      msg.textContent = ex.message || "Error al subir. Mandanos la foto por WhatsApp.";
    }
    btn.disabled = false;
    btn.textContent = "Enviar comprobante";
  });
})();
