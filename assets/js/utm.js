/**
 * Guarda UTMs en sessionStorage ('tn_utm') y, si hay utm_source o utm_campaign,
 * los suma al final del texto de WhatsApp al hacer clic: " [utm:instagram/parejas]".
 */
(function () {
  const q = new URLSearchParams(location.search);
  const keys = ["utm_source", "utm_medium", "utm_campaign", "utm_content"];
  let out = {};
  keys.forEach((k) => {
    const v = q.get(k);
    if (v) out[k] = v;
  });
  try {
    if (Object.keys(out).length) {
      sessionStorage.setItem("tn_utm", JSON.stringify(out));
    }
  } catch (_) {}

  function leerUtm() {
    try {
      return JSON.parse(sessionStorage.getItem("tn_utm") || "null");
    } catch (_) {
      return null;
    }
  }

  document.addEventListener(
    "click",
    function (ev) {
      const a = ev.target && ev.target.closest ? ev.target.closest('a[href*="wa.me/"]') : null;
      if (!a) return;
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
