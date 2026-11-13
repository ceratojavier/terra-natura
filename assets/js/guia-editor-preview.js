(() => {
  const params = new URLSearchParams(location.search);
  const editorPreview = params.get("tn-editor-preview") === "1";
  const API = "https://api.alpinasterranatura.com.ar/api/public/guia-experiencia";
  const DEFAULTS = "https://alpinasterranatura.com.ar/assets/data/guia-experiencia-default.json";
  const bindings = [];
  let payload = null;
  const bind = (selector, sectionKey, field = "text") => {
    document.querySelectorAll(selector).forEach((element) => {
      element.dataset.tnGuideEditor = `${sectionKey}:${field}`;
      bindings.push({ element, sectionKey, field });
    });
  };
  const bindBackgroundButton = (selector, sectionKey, label) => {
    const element = document.querySelector(selector);
    if (!element) return;
    element.style.position ||= "relative";
    bindings.push({ background: element, sectionKey, field: "image" });
    if (!editorPreview || element.querySelector(`[data-tn-guide-editor="${sectionKey}:image"]`)) return;
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `📷 ${label}`;
    button.dataset.tnGuideEditor = `${sectionKey}:image`;
    button.style.cssText = "position:absolute;right:14px;top:14px;z-index:20;border:1px solid #0b764a;border-radius:999px;background:#fff;color:#0b3c29;padding:7px 10px;font:600 12px system-ui;cursor:pointer";
    element.appendChild(button);
  };

  bind("#bienvenida .hero-content h1", "hero", "text");
  bind("#bienvenida .hero-content p", "hero", "intro");
  bind(".welcome-strip b", "welcome", "title");
  bind(".welcome-strip p", "welcome", "intro");
  bind("#explorar .section-heading h2", "explore_heading", "text");
  bind("#explorar .section-heading p", "explore_heading", "intro");
  bind(".featured-band .featured-copy h2", "featured", "text");
  bind(".featured-band .featured-copy p", "featured", "intro");
  bind("#informacion .section-heading h2", "stay_heading", "text");
  bind("#informacion .section-heading p", "stay_heading", "intro");
  bindBackgroundButton("#bienvenida", "hero", "Cambiar portada");
  bindBackgroundButton(".featured-band", "featured", "Cambiar foto");
  bind(".planner-intro h2", "planner", "text");
  bind(".planner-intro p", "planner", "intro");
  bind(".planner-top h3", "planner", "body");
  bind(".closing-cta h2", "closing", "text");
  bind(".closing-cta p", "closing", "intro");
  bind("footer > span:nth-of-type(1)", "footer_location", "text");
  bind("footer > span:nth-of-type(2)", "footer_note", "text");
  const bindStay = (selector, field) => document.querySelectorAll(selector).forEach((el) => {
    if (editorPreview) el.dataset.tnGuideStayField = field;
  });
  bindStay(".stay-bubble-panel > header b", "bubble_title");
  bindStay(".stay-bubble-panel > header p", "bubble_intro");
  bindStay(".bubble-callout.water p", "water_notice");
  bindStay(".stay-bubble-panel .wifi-note", "wifi_note");
  bindStay("#informacion .stay-card.important p", "water_notice");
  document.querySelectorAll("#informacion .stay-card:not(.important) > div > p").forEach((el, index) => {
    if (editorPreview) el.dataset.tnGuideStayField = `amenities.${index}`;
  });

  const categoryKeys = ["category_cerca", "category_naturaleza", "category_balnearios", "category_gastronomia", "category_noche", "category_familia", "category_lluvia", "category_servicios"];
  document.querySelectorAll("#recomendaciones .place-group").forEach((group, index) => {
    const key = categoryKeys[index];
    if (!key) return;
    group.querySelectorAll(".place-group-title").forEach((el) => bindElement(el, key, "text"));
    group.querySelectorAll(":scope > p").forEach((el) => bindElement(el, key, "intro"));
  });
  function bindElement(element, sectionKey, field) {
    element.dataset.tnGuideEditor = `${sectionKey}:${field}`;
    bindings.push({ element, sectionKey, field });
  }

  const deepMerge = (base, over) => {
    if (!base || typeof base !== "object" || Array.isArray(base) || !over || typeof over !== "object" || Array.isArray(over)) return over === undefined ? base : over;
    const out = { ...base };
    Object.entries(over).forEach(([key, value]) => { out[key] = value && typeof value === "object" && !Array.isArray(value) ? deepMerge(base[key], value) : value; });
    return out;
  };
  const sectionMap = () => new Map((payload?.sections || []).map((section) => [section.section_key, section]));
  const text = (node, value) => { if (node && typeof value === "string" && value.trim()) node.textContent = value; };
  const apply = () => {
    if (!payload) return;
    const sections = sectionMap();
    bindings.forEach(({ element, background, sectionKey, field }) => {
      const section = sections.get(sectionKey);
      if (!section) return;
      if (field === "text") text(element, [section.title, section.subtitle].filter(Boolean).join(" "));
      if (field === "intro") text(element, section.intro);
      if (field === "title") text(element, section.title);
      if (field === "subtitle") text(element, section.subtitle);
      if (field === "body") text(element, section.body);
      if (["left", "center", "right"].includes(section.text_align)) element.style.textAlign = section.text_align;
      if (typeof section.font_family === "string" && section.font_family.length < 100) element.style.fontFamily = section.font_family;
      if (field === "image" && section.image_url) {
        const image = section.image_url.startsWith("http") ? section.image_url : `https://alpinasterranatura.com.ar/${section.image_url.replace(/^\//, "")}`;
        if (background) background.style.backgroundImage = `linear-gradient(90deg, rgba(18,35,28,.76), rgba(18,35,28,.16)), url("${image}")`;
      }
    });
    const stay = payload.stay || {};
    text(document.querySelector(".stay-bubble-panel > header b"), stay.bubble_title);
    text(document.querySelector(".stay-bubble-panel > header p"), stay.bubble_intro);
    text(document.querySelector(".bubble-callout.water p"), stay.water_notice);
    document.querySelectorAll(".stay-bubble-panel .wifi-note, #informacion .stay-card-wifi .wifi-note").forEach((node) => text(node, stay.wifi_note));
    const lists = [...document.querySelectorAll(".stay-bubble-panel section ul")];
    [[stay.amenities, lists[0]], [stay.tips, lists[1]]].forEach(([items, list]) => {
      if (!Array.isArray(items) || !list || items.join("\u0000") === [...list.children].map((li) => li.textContent || "").join("\u0000")) return;
      list.replaceChildren(...items.map((value) => { const li = document.createElement("li"); li.textContent = value; return li; }));
    });
    bindRecommendations();
  };
  const norm = (s) => (s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim().toLowerCase();
  function bindRecommendations() {
    if (!payload?.recommendations?.length) return;
    document.querySelectorAll("#recomendaciones .place-card").forEach((card) => {
      const title = card.querySelector("h3");
      const rec = payload.recommendations.find((item) => norm(item.name) === norm(title?.textContent));
      if (!rec) return;
      if (editorPreview) {
        card.dataset.tnGuideRecommendation = rec.id;
        card.querySelector(".place-image")?.setAttribute("data-tn-guide-rec-image", rec.id);
      }
      const locality = card.querySelector(".place-locality");
      if (locality && rec.locality) locality.textContent = rec.locality;
      text(title, rec.name);
      text(card.querySelector(":scope > .place-content > p"), rec.short_description);
      const image = card.querySelector(".place-image img");
      if (image && rec.image_url) image.src = rec.image_url.startsWith("http") ? rec.image_url : `https://alpinasterranatura.com.ar/${rec.image_url.replace(/^\//, "")}`;
      const detail = card.querySelector(".place-details > p");
      if (detail) text(detail, rec.description);
      const tags = card.querySelector(".place-tags");
      if (tags && Array.isArray(rec.tags) && rec.tags.join("\u0000") !== [...tags.children].map((span) => span.textContent || "").join("\u0000")) tags.replaceChildren(...rec.tags.map((value) => { const span = document.createElement("span"); span.textContent = value; return span; }));
    });
  }

  if (editorPreview) {
    const style = document.createElement("style");
    style.textContent = "[data-tn-guide-editor],[data-tn-guide-stay-field],[data-tn-guide-recommendation],[data-tn-guide-rec-image]{cursor:pointer!important;outline:1px dashed rgba(11,118,74,.6);outline-offset:3px;-webkit-user-select:none;user-select:none}[data-tn-guide-editor]:hover,[data-tn-guide-stay-field]:hover,[data-tn-guide-recommendation]:hover,[data-tn-guide-rec-image]:hover{outline:2px solid #0b764a!important;outline-offset:3px;filter:brightness(1.03)}";
    document.head.appendChild(style);
  }
  document.addEventListener("click", (event) => {
    const node = event.target instanceof Element ? event.target : null;
    if (!node) return;
    const stayField = node.closest("[data-tn-guide-stay-field]")?.dataset.tnGuideStayField;
    if (editorPreview && stayField) {
      event.preventDefault(); event.stopPropagation();
      window.parent.postMessage({ type: "tn-guide-editor-select", stayField }, "*");
      return;
    }
    const card = node.closest("[data-tn-guide-recommendation]");
    if (editorPreview && card) {
      event.preventDefault(); event.stopPropagation();
      window.parent.postMessage({ type: "tn-guide-editor-select", recommendationId: card.dataset.tnGuideRecommendation, field: node.closest("[data-tn-guide-rec-image]") ? "image" : "text" }, "*");
      return;
    }
    if (!editorPreview) return;
    const target = node.closest("[data-tn-guide-editor]");
    if (!target) {
      const link = node.closest("a");
      if (link) { event.preventDefault(); event.stopPropagation(); }
      return;
    }
    event.preventDefault(); event.stopPropagation();
    const [sectionKey, field] = target.dataset.tnGuideEditor.split(":");
    window.parent.postMessage({ type: "tn-guide-editor-select", sectionKey, field }, "*");
  }, true);

  const start = async () => {
    try {
      const [defaultsResponse, apiResponse] = await Promise.all([
        fetch(DEFAULTS, { cache: "no-store" }).catch(() => null),
        fetch(API, { cache: "no-store" }).catch(() => null),
      ]);
      const defaults = defaultsResponse?.ok ? await defaultsResponse.json() : {};
      const live = apiResponse?.ok ? await apiResponse.json() : {};
      payload = deepMerge(defaults, live);
      apply();
    } catch { /* La guía sigue funcionando con el contenido embebido si la API no responde. */ }
  };
  void start();
  const observer = new MutationObserver(() => { bindRecommendations(); });
  if (editorPreview) observer.observe(document.body, { childList: true, subtree: true });
})();
