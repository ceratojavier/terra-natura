(function () {
  const params = new URLSearchParams(location.search);
  const reservaId = params.get("reserva_id") || "";
  const senia = params.get("senia") || "";
  const resumen = document.getElementById("sim-resumen");
  const btn = document.getElementById("sim-btn-pagar");
  const msg = document.getElementById("sim-msg");

  if (!reservaId || !btn) return;

  const API_FALLBACK = "https://api.alpinasterranatura.com.ar";

  function apiBase() {
    return (window.__TN_API_BASE || API_FALLBACK).replace(/\/$/, "");
  }

  async function apiFetch(path, options) {
    const res = await fetch(`${apiBase()}${path}`, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options && options.headers),
      },
    });
    if (!res.ok) {
      let detail = `HTTP ${res.status}`;
      try {
        const j = await res.json();
        detail = j.detail || detail;
      } catch (_) {}
      throw new Error(typeof detail === "string" ? detail : "Error en el servidor");
    }
    return res.json();
  }

  fetch("./assets/data/site-config.json?v=2")
    .then(function (r) {
      return r.ok ? r.json() : null;
    })
    .then(function (cfg) {
      if (cfg && cfg.apiBase) window.__TN_API_BASE = cfg.apiBase;
    })
    .finally(function () {
      resumen.hidden = false;
      resumen.className = "result ok";
      resumen.innerHTML =
        `<strong>Pre-reserva creada</strong><br>` +
        `Código interno: <code>${reservaId.slice(0, 8)}…</code><br>` +
        (senia ? `Seña de prueba: <strong>$${Number(senia).toLocaleString("es-AR")}</strong>` : "");
      btn.disabled = false;
    });

  btn.addEventListener("click", async function () {
    btn.disabled = true;
    btn.textContent = "Confirmando…";
    msg.hidden = true;
    try {
      const out = await apiFetch("/api/public/simular-pago-sena", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reserva_id: reservaId }),
      });
      location.href = `./reserva-exito.html?reserva_id=${encodeURIComponent(
        out.reserva_id || reservaId
      )}&codigo=${encodeURIComponent(out.codigo || "")}&sim=1`;
    } catch (err) {
      btn.disabled = false;
      btn.textContent = "Simular seña pagada";
      msg.hidden = false;
      msg.textContent = err.message || "No se pudo simular el pago.";
    }
  });
})();
