(() => {
  const params = new URLSearchParams(location.search);
  const editorPreview = params.get("tn-editor-preview") === "1";
  const API = "https://api.alpinasterranatura.com.ar/api/sitio/guia-experiencia";
  const groups = ["category_cerca", "category_naturaleza", "category_balnearios", "category_gastronomia", "category_noche", "category_familia", "category_lluvia", "category_servicios"];
  const bindings = [];
  const bind = (selector, sectionKey, field) => {
    document.querySelectorAll(selector).forEach((element) => {
      if (editorPreview) element.dataset.tnGuideEditor = `${sectionKey}:${field}`;
      bindings.push({ element, sectionKey, field });
    });
  };
  bind("#bienvenida .hero-content h1", "hero", "text");
  bind("#bienvenida .hero-content p", "hero", "intro");
  bind(".welcome-strip", "welcome", "text");
  bind("#explorar .section-heading h2", "explore_heading", "text");
  bind("#explorar .section-heading p", "explore_heading", "intro");
  bind(".featured-band .featured-copy h2", "featured", "text");
  bind(".featured-band .featured-copy p", "featured", "intro");
  const bindBackgroundButton = (selector, sectionKey, label) => {
    const element = document.querySelector(selector);
    if (!element) return;
    element.style.position ||= "relative";
    bindings.push({ background: element, sectionKey, field: "image" });
    if (!editorPreview) return;
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `📷 ${label}`;
    button.dataset.tnGuideEditor = `${sectionKey}:image`;
    button.style.cssText = "position:absolute;right:14px;top:14px;z-index:20;border:1px solid #0b764a;border-radius:999px;background:#fff;color:#0b3c29;padding:7px 10px;font:600 12px system-ui;cursor:pointer";
    element.appendChild(button);
    bindings.push({ element: button, background: element, sectionKey, field: "image" });
  };
  bindBackgroundButton("#bienvenida", "hero", "Cambiar portada");
  bindBackgroundButton(".featured-band", "featured", "Cambiar foto");
  bind("#informacion .section-heading h2", "stay_heading", "text");
  bind("#informacion .section-heading p", "stay_heading", "intro");
  document.querySelectorAll("#recomendaciones .place-group").forEach((group, index) => {
    const key = groups[index];
    if (!key) return;
    group.querySelectorAll(".place-group-title").forEach((el) => {
      el.dataset.tnGuideEditor = `${key}:text`;
      bindings.push({ element: el, sectionKey: key, field: "text" });
    });
    group.querySelectorAll(":scope > p").forEach((el) => {
      el.dataset.tnGuideEditor = `${key}:intro`;
      bindings.push({ element: el, sectionKey: key, field: "intro" });
    });
  });

  const setText = (element, title, subtitle) => {
    element.textContent = [title, subtitle].filter(Boolean).join(" ");
  };
  const apply = async () => {
    try {
      const response = await fetch(API, { cache: "no-store" });
      if (!response.ok) return;
      const payload = await response.json();
      const sections = new Map((payload.sections || []).map((section) => [section.section_key, section]));
      bindings.forEach(({ element, background, sectionKey, field }) => {
        const section = sections.get(sectionKey);
        if (!section) return;
        if (field === "text") setText(element, section.title || "", section.subtitle || "");
        if (field === "intro" && section.intro) element.textContent = section.intro;
        if (["left", "center", "right"].includes(section.text_align)) element.style.textAlign = section.text_align;
        if (typeof section.font_family === "string" && section.font_family.length < 100) element.style.fontFamily = section.font_family;
        if (field === "image" && section.image_url) {
          const image = section.image_url.startsWith("http") ? section.image_url : `https://alpinasterranatura.com.ar/${section.image_url.replace(/^\//, "")}`;
          if (background) background.style.backgroundImage = `linear-gradient(90deg, rgba(18,35,28,.76), rgba(18,35,28,.16)), url("${image}")`;
        }
      });
    } catch { /* La guía pública mantiene el contenido embebido si no hay red. */ }
  };
  void apply();
  const observer = new MutationObserver(() => { bindings.forEach(({ element, sectionKey, field }) => {
    if (!element.isConnected || element.dataset.tnGuideEditor) return;
    element.dataset.tnGuideEditor = `${sectionKey}:${field}`;
  }); });
  if (editorPreview) observer.observe(document.body, { childList: true, subtree: true });
  if (editorPreview) {
    const style = document.createElement("style");
    style.textContent = "[data-tn-guide-editor]{cursor:pointer!important;outline:1px dashed rgba(11,118,74,.6);outline-offset:3px}[data-tn-guide-editor]:hover{outline:2px solid #0b764a!important;outline-offset:3px;filter:brightness(1.03)}";
    document.head.appendChild(style);
  }
  if (editorPreview) document.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target.closest("[data-tn-guide-editor]") : null;
    if (!target) return;
    event.preventDefault();
    event.stopPropagation();
    const [sectionKey, field] = target.dataset.tnGuideEditor.split(":");
    window.parent.postMessage({ type: "tn-guide-editor-select", sectionKey, field }, "*");
  }, true);
})();
