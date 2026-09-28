(function () {
  const params = new URLSearchParams(location.search);
  const reservaId =
    params.get("reserva_id") ||
    params.get("external_reference") ||
    params.get("preference_id") ||
    "";
  const codigoParam = params.get("codigo") || "";
  const titulo = document.querySelector("h1");
  const parrafo = document.querySelector("main p");
  const extra = document.getElementById("reserva-exito-detalle");

  if (!reservaId || !extra) return;

  const API_FALLBACK = "https://api.alpinasterranatura.com.ar";

  function apiBase() {
    return (window.__TN_API_BASE || API_FALLBACK).replace(/\/$/, "");
  }

  fetch("./assets/data/site-config.json?v=2")
    .then(function (r) {
      return r.ok ? r.json() : null;
    })
    .then(function (cfg) {
      if (cfg && cfg.apiBase) window.__TN_API_BASE = cfg.apiBase;
      return fetch(`${apiBase()}/api/public/reserva/${encodeURIComponent(reservaId)}/estado`, {
        headers: { Accept: "application/json" },
      });
    })
    .then(function (r) {
      return r.ok ? r.json() : null;
    })
    .then(function (data) {
      if (!data) {
        if (codigoParam && parrafo) {
          parrafo.textContent = `Tu código de reserva es ${codigoParam}. Te contactamos con los detalles de llegada.`;
        }
        return;
      }
      extra.hidden = false;
      extra.className = "result ok";
      const codigo = data.codigo || codigoParam;
      if (titulo && data.confirmada) titulo.textContent = "¡Reserva confirmada!";
      extra.innerHTML =
        `<strong>Código:</strong> ${codigo}<br>` +
        `<strong>${data.unidad_nombre}</strong> · ${data.check_in} → ${data.check_out}<br>` +
        (data.confirmada
          ? "Tu seña quedó registrada. Te escribimos con indicaciones para llegar."
          : "Estamos procesando el pago. Si en unos minutos no ves confirmación, escribinos por WhatsApp.");
      if (parrafo && data.confirmada) {
        parrafo.textContent = "Gracias por reservar directo con nosotros.";
      }
    })
    .catch(function () {
      if (codigoParam && parrafo) {
        parrafo.textContent = `Tu código de reserva es ${codigoParam}. Te contactamos con los detalles de llegada.`;
      }
    });
})();
