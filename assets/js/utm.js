/**
 * Guarda UTMs en sessionStorage ('tn_utm') y, si hay utm_source o utm_campaign,
 * los suma al final del texto de WhatsApp al hacer clic: " [utm:instagram/parejas]".
 */
(function () {
  const q = new URLSearchParams(location.search);
  const keys = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "fbclid", "gclid"];
  let out = {};
  keys.forEach((k) => {
    const v = q.get(k);
    if (v) out[k] = v;
  });
  function leerUtm() {
    try {
      return JSON.parse(sessionStorage.getItem("tn_utm") || "null");
    } catch (_) {
      return null;
    }
  }

  function visitorId() {
    try {
      let id = localStorage.getItem("tn_vid");
      if (!id) {
        id = "v-" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
        localStorage.setItem("tn_vid", id);
      }
      return id;
    } catch (_) { return null; }
  }

  function origenReferrer() {
    try { return document.referrer ? new URL(document.referrer).origin : ""; } catch (_) { return ""; }
  }

  function leerPrimeraVisita() {
    try { return JSON.parse(localStorage.getItem("tn_utm_first") || "null"); } catch (_) { return null; }
  }

  // Cobertura para landings que no cargan tn-atribucion.js.
  try {
    if (!window.TNAtribucion) {
      const saved = leerUtm() || {};
      if (Object.keys(out).length || !saved.visitor_id) {
        const current = {
          ...saved,
          ...out,
          landing_page: Object.keys(out).length ? location.pathname : (saved.landing_page || location.pathname),
          referrer: Object.keys(out).length ? origenReferrer() : (saved.referrer || origenReferrer()),
          visitor_id: saved.visitor_id || visitorId(),
          canal_contacto: "web",
          ts: new Date().toISOString(),
        };
        sessionStorage.setItem("tn_utm", JSON.stringify(current));
        if (!leerPrimeraVisita()) localStorage.setItem("tn_utm_first", JSON.stringify(current));
      }
    }
  } catch (_) {}

  function payloadApi() {
    if (window.TNAtribucion && typeof window.TNAtribucion.payloadApi === "function") {
      return window.TNAtribucion.payloadApi();
    }
    const saved = leerUtm() || {};
    const out = {};
    ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "fbclid", "gclid"].forEach((k) => {
      out[k] = saved[k] || null;
    });
    out.visitor_id = visitorId();
    out.landing_page = saved.landing_page || location.pathname;
    out.referrer = saved.referrer || origenReferrer();
    out.primera_visita = leerPrimeraVisita();
    out.canal_contacto = "web";
    return out;
  }

  function track(eventType) {
    const body = JSON.stringify({ event_type: eventType, page_path: location.pathname, atribucion: payloadApi() });
    const base = (window.TN_SITE_CONFIG && window.TN_SITE_CONFIG.apiBase) ||
      ((location.hostname === "localhost" || location.hostname === "127.0.0.1") ? location.origin : "https://api.alpinasterranatura.com.ar");
    const url = base.replace(/\/$/, "") + "/api/public/medicion/evento";
    try {
      const blob = new Blob([body], { type: "application/json" });
      if (navigator.sendBeacon && navigator.sendBeacon(url, blob)) return;
    } catch (_) {}
    fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body, keepalive: true, mode: "cors" }).catch(function () {});
  }
  window.TNMedicion = { track };
  track(location.pathname.toLowerCase().includes("reserv") ? "booking_page_view" : "page_view");

  document.addEventListener(
    "click",
    function (ev) {
      const a = ev.target && ev.target.closest ? ev.target.closest('a[href*="wa.me/"]') : null;
      if (!a) return;
      track("whatsapp_click");
      const utm = leerUtm();
      if (!utm || (!utm.utm_source && !utm.utm_campaign)) return;
      let url;
      try {
        url = new URL(a.href);
      } catch (_) {
        return;
      }
      const text = url.searchParams.get("text") || "";
      if (text.indexOf("[utm:") !== -1) return;
      const limpio = (s) => String(s || "-").replace(/[\[\]\s]+/g, "-").slice(0, 40);
      const tag = " [utm:" + limpio(utm.utm_source) + "/" + limpio(utm.utm_campaign) + "]";
      url.searchParams.set("text", text + tag);
      // wa.me espera %20 para los espacios (URLSearchParams usa "+").
      const qs = [];
      url.searchParams.forEach(function (v, k) {
        qs.push(encodeURIComponent(k) + "=" + encodeURIComponent(v));
      });
      a.href = url.origin + url.pathname + "?" + qs.join("&");
    },
    true
  );
})();
