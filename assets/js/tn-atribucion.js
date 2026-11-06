/**
 * Atribución web Terra Natura: primera visita + sesión actual → API pública y reservas.
 */
(function () {
  const KEYS = [
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
    "fbclid",
    "gclid",
  ];

  function leerQuery() {
    const q = new URLSearchParams(location.search);
    const out = {};
    KEYS.forEach(function (k) {
      const v = q.get(k);
      if (v) out[k] = v;
    });
    return out;
  }

  function visitorId() {
    try {
      let id = localStorage.getItem("tn_vid");
      if (!id) {
        id = "v-" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
        localStorage.setItem("tn_vid", id);
      }
      return id;
    } catch (_) {
      return null;
    }
  }

  function guardar() {
    const q = leerQuery();
    const payload = {
      ...q,
      landing_page: location.pathname.slice(0, 500),
      referrer: (() => { try { return document.referrer ? new URL(document.referrer).origin : ""; } catch (_) { return ""; } })(),
      visitor_id: visitorId(),
      canal_contacto: "web",
      ts: new Date().toISOString(),
    };
    try {
      if (Object.keys(q).length || !sessionStorage.getItem("tn_utm")) {
        sessionStorage.setItem("tn_utm", JSON.stringify(payload));
      }
      if (Object.keys(q).length && !localStorage.getItem("tn_utm_first")) {
        localStorage.setItem("tn_utm_first", JSON.stringify(payload));
      }
    } catch (_) {}
  }

  function leerAtribucion() {
    try {
      const cur = JSON.parse(sessionStorage.getItem("tn_utm") || "null");
      const first = JSON.parse(localStorage.getItem("tn_utm_first") || "null");
      const base = cur && typeof cur === "object" ? { ...cur } : {};
      if (first && typeof first === "object") {
        base.primera_visita = first;
      }
      return Object.keys(base).length ? base : null;
    } catch (_) {
      return null;
    }
  }

  guardar();

  window.TNAtribucion = {
    leer: leerAtribucion,
    payloadApi: function () {
      const a = leerAtribucion();
      if (!a) return null;
      const first = a.primera_visita && typeof a.primera_visita === "object" ? a.primera_visita : null;
      return {
        utm_source: a.utm_source || null,
        utm_medium: a.utm_medium || null,
        utm_campaign: a.utm_campaign || null,
        utm_content: a.utm_content || null,
        utm_term: a.utm_term || null,
        fbclid: a.fbclid || null,
        gclid: a.gclid || null,
        landing_page: a.landing_page ? String(a.landing_page).split(/[?#]/, 1)[0] : null,
        referrer: (() => { try { return a.referrer ? new URL(a.referrer).origin : null; } catch (_) { return null; } })(),
        visitor_id: a.visitor_id || null,
        primera_visita: first ? {
          utm_source: first.utm_source || null,
          utm_medium: first.utm_medium || null,
          utm_campaign: first.utm_campaign || null,
          utm_content: first.utm_content || null,
          utm_term: first.utm_term || null,
          fbclid: first.fbclid || null,
          gclid: first.gclid || null,
          visitor_id: first.visitor_id || null,
          landing_page: first.landing_page ? String(first.landing_page).split(/[?#]/, 1)[0] : null,
          referrer: (() => { try { return first.referrer ? new URL(first.referrer).origin : null; } catch (_) { return null; } })(),
          ts: first.ts || null,
        } : null,
        canal_contacto: "web",
      };
    },
  };
})();
