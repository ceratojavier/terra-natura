(function () {
  const API = "https://api.alpinasterranatura.com.ar";
  function apiBase() {
    if (["alpinasterranatura.com.ar", "www.alpinasterranatura.com.ar"].includes(location.hostname)) return API;
    if (location.protocol.startsWith("http") && !location.hostname.includes("github.io")) return location.origin;
    return API;
  }
  const groupId = new URLSearchParams(location.search).get("grupo") || "";
  const root = document.getElementById("grupo-unidades");
  const summary = document.getElementById("grupo-resumen");
  const bank = document.getElementById("grupo-banco");
  const error = document.getElementById("grupo-error");
  const plazo = document.getElementById("grupo-plazo");
  const finalStep = document.getElementById("grupo-datos-finales");
  const confirmation = document.getElementById("grupo-confirmacion");
  const totalBox = document.getElementById("grupo-total");
  const fmt = (n) => new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(Number(n) || 0);
  function el(tag, text, cls) {
    const node = document.createElement(tag);
    if (text != null) node.textContent = text;
    if (cls) node.className = cls;
    return node;
  }
  function appendBankItem(parent, label, value) {
    if (!value) return;
    const item = el("div", null, "checkout-bank-item");
    item.append(el("span", label));
    const strong = el("strong", value);
    item.append(strong);
    if (["Alias", "CBU / CVU"].includes(label)) {
      const copy = el("button", "Copiar", "checkout-copy");
      copy.type = "button";
      copy.addEventListener("click", async () => {
        try { await navigator.clipboard.writeText(value); copy.textContent = "Copiado"; } catch (_) { copy.textContent = value; }
      });
      strong.append(" ", copy);
    }
    parent.append(item);
  }
  function maybeShowFinalStep() {
    const forms = Array.from(root.querySelectorAll("form[data-reserva-id]"));
    const allReceived = forms.length > 0 && forms.every((form) => form.dataset.comprobanteOk === "true");
    finalStep.hidden = !allReceived;
  }
  function buildFinalStep(reservas) {
    finalStep.replaceChildren(el("span", "\u2713", "checkout-success-icon"), el("p", "PASO FINAL \u00b7 DATOS DEL TITULAR", "checkout-eyebrow"), el("h2", "Comprobantes recibidos"), el("p", "Complet\u00e1 los datos del pasajero principal. Se guardar\u00e1n en cada pre-reserva y la estad\u00eda seguir\u00e1 pendiente hasta que revisemos el pago."));
    const form = document.createElement("form");
    form.id = "grupo-datos-form";
    form.className = "checkout-profile-form";
    const grid = el("div", null, "checkout-grid");
    const fields = [["dni", "DNI", "text", 7, 12], ["domicilio", "Domicilio", "text", 5, 160], ["localidad", "Localidad", "text", 2, 100], ["provincia", "Provincia", "text", 2, 100], ["email", "Email para el voucher (opcional)", "email", 0, 120]];
    fields.forEach(([name, labelText, type, min, max]) => {
      const label = el("label", labelText, name === "domicilio" || name === "email" ? "checkout-grid-wide" : "");
      const input = document.createElement("input");
      input.name = name; input.type = type; input.required = name !== "email";
      input.minLength = Number(min); input.maxLength = Number(max);
      if (name === "dni") { input.inputMode = "numeric"; input.pattern = "[0-9]{7,12}"; }
      if (name === "domicilio") input.autocomplete = "street-address";
      if (name === "localidad") input.autocomplete = "address-level2";
      if (name === "provincia") { input.autocomplete = "address-level1"; input.value = "C\u00f3rdoba"; }
      if (name === "email") input.autocomplete = "email";
      label.append(input); grid.append(label);
    });
    const submit = el("button", "Guardar datos y finalizar", "checkout-submit"); submit.type = "submit";
    const status = el("p", "", "checkout-upload-error"); status.id = "grupo-datos-error"; status.hidden = true; status.setAttribute("role", "alert");
    form.append(grid, status, submit);
    form.addEventListener("submit", async (event) => {
      event.preventDefault(); status.hidden = true; submit.disabled = true; submit.textContent = "Guardando datos\u2026";
      const data = new FormData(form);
      const payload = { dni: String(data.get("dni") || "").replace(/\D/g, ""), domicilio: String(data.get("domicilio") || "").trim(), localidad: String(data.get("localidad") || "").trim(), provincia: String(data.get("provincia") || "").trim(), email: String(data.get("email") || "").trim() || null };
      try {
        const results = await Promise.all(reservas.map(async (r) => {
          const response = await fetch(`${apiBase()}/api/public/reserva/${encodeURIComponent(r.reserva_id)}/datos-pasajero`, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify({ codigo: r.codigo, ...payload }) });
          const body = await response.json().catch(() => ({}));
          if (!response.ok) throw new Error(body.detail || `No pudimos guardar los datos del c\u00f3digo ${r.codigo}.`);
          return body;
        }));
        if (results.length !== reservas.length || results.some((r) => !["pre_reserva", "pendiente_pago"].includes(r.estado))) throw new Error("Los datos se guardaron, pero alguna unidad ya cambi\u00f3 de estado. Contactanos para confirmar el grupo.");
        finalStep.hidden = true;
        document.getElementById("grupo-codigos").textContent = `C\u00f3digos de pre-reserva: ${reservas.map((r) => r.codigo).join(" \u00b7 ")}`;
        confirmation.hidden = false;
      } catch (e) {
        status.textContent = e.message || "No pudimos guardar los datos. Revis\u00e1 la conexi\u00f3n e intent\u00e1 otra vez.";
        status.hidden = false; submit.disabled = false; submit.textContent = "Guardar datos y finalizar";
      }
    });
    finalStep.append(form);
  }
  function render(data) {
    if (!data || !Array.isArray(data.reservas) || !data.reservas.length) throw new Error("No encontramos el detalle de este grupo de reservas.");
    if (data.texto_plazo) plazo.textContent = data.texto_plazo;
    else if (data.plazo_horas) plazo.textContent = `Transfer\u00ed las se\u00f1as dentro de las pr\u00f3ximas ${data.plazo_horas} horas para mantener las fechas bloqueadas.`;
    summary.replaceChildren();
    const heading = el("div", null, "checkout-panel-title");
    const badge = el("span", "01", "checkout-step");
    const headingText = el("div"); headingText.append(el("h2", `Resumen \u00b7 ${data.reservas.length} caba\u00f1as`), el("p", "Unidades para las mismas fechas"));
    heading.append(badge, headingText); summary.append(heading); summary.hidden = false;
    totalBox.replaceChildren(el("p", "Tu estad\u00eda", "checkout-eyebrow"), el("h2", fmt(data.total)));
    totalBox.append(el("p", `Total de la estad\u00eda \u00b7 ${fmt(data.total)}`, "checkout-price-lines"), el("p", `Se\u00f1a total (50 %) \u00b7 ${fmt(data.senia_total)}`, "checkout-deposit"), el("p", data.reservas.map((r) => `${r.unidad_nombre || r.unidad_id}: ${r.check_in} \u2192 ${r.check_out}`).join("\n"), "checkout-deadline"));
    totalBox.hidden = false;
    bank.replaceChildren(el("h2", "Transferencia bancaria"), el("p", "Transfer\u00ed la se\u00f1a de cada unidad e indic\u00e1 el c\u00f3digo correspondiente en cada comprobante."));
    const bankGrid = el("div", null, "checkout-bank-grid"); const dp = data.datos_pago || {};
    appendBankItem(bankGrid, "Titular", dp.titular || data.titular);
    appendBankItem(bankGrid, "CUIT / CUIL", dp.cuit || dp.cuil || data.cuil);
    appendBankItem(bankGrid, "Alias", dp.alias || data.alias || data.alias_transferencia);
    appendBankItem(bankGrid, "CBU / CVU", dp.cbu || dp.cbu_cvu || data.cbu);
    appendBankItem(bankGrid, "Banco / billetera", dp.banco || dp.medio || data.banco);
    if (bankGrid.childElementCount) bank.append(bankGrid); else bank.append(el("p", "Los datos bancarios no est\u00e1n cargados. Escribinos por WhatsApp antes de transferir.", "checkout-bank-note"));
    bank.hidden = false; root.replaceChildren();
    data.reservas.forEach((r) => {
      const card = el("article", null, "checkout-panel checkout-group-unit");
      card.append(el("h2", r.unidad_nombre || r.unidad_id), el("p", `Titular: ${r.titular || "Titular de la reserva"}`), el("p", `${r.check_in} \u2192 ${r.check_out} \u00b7 C\u00f3digo ${r.codigo}`), el("p", `Total: ${fmt(r.total)} \u00b7 Se\u00f1a: ${fmt(r.senia)}`));
      if (r.link_mercadopago && ["mercadopago", "simulador"].includes(r.modo_pago)) {
        const pay = el("a", r.modo_pago === "simulador" ? "Abrir simulador de pago" : "Pagar esta se\u00f1a con Mercado Pago", "checkout-method checkout-method-primary");
        pay.href = r.link_mercadopago; pay.target = "_blank"; pay.rel = "noopener noreferrer"; card.append(pay);
      }
      const form = document.createElement("form"); form.dataset.reservaId = r.reserva_id; form.dataset.codigo = r.codigo; form.dataset.comprobanteOk = String(Boolean(r.comprobante_recibido));
      const label = el("label", "Comprobante de esta caba\u00f1a (JPG, PNG, WebP o PDF)", "checkout-drop");
      const file = document.createElement("input"); file.type = "file"; file.accept = "image/jpeg,image/png,image/webp,application/pdf,.jpg,.jpeg,.png,.webp,.pdf"; file.required = true; label.append(file);
      const submit = el("button", r.comprobante_recibido ? "Comprobante recibido" : "Enviar comprobante", "checkout-submit"); submit.type = "submit";
      if (r.comprobante_recibido) { file.disabled = true; submit.disabled = true; }
      const status = el("p", r.comprobante_recibido ? "Ya recibimos un comprobante pendiente de revisi\u00f3n." : "Adjunt\u00e1 el comprobante de esta unidad.", "checkout-upload-error"); status.hidden = !r.comprobante_recibido;
      form.append(label, submit, status); card.append(form); root.append(card);
    });
    buildFinalStep(data.reservas); maybeShowFinalStep();
    if (data.reservas.every((r) => r.datos_pasajero_completos) && data.reservas.every((r) => r.comprobante_recibido)) {
      finalStep.hidden = true; document.getElementById("grupo-codigos").textContent = `C\u00f3digos de pre-reserva: ${data.reservas.map((r) => r.codigo).join(" \u00b7 ")}`; confirmation.hidden = false;
    }
  }
  root.addEventListener("submit", async (event) => {
    const form = event.target.closest("form[data-reserva-id]"); if (!form) return;
    event.preventDefault(); const file = form.querySelector('input[type="file"]').files[0]; if (!file) return;
    const status = form.querySelector(".checkout-upload-error");
    if (file.size > 8_000_000) { status.textContent = "El archivo supera el m\u00e1ximo de 8 MB."; status.hidden = false; return; }
    const fd = new FormData(); fd.append("codigo", form.dataset.codigo); fd.append("archivo", file);
    const button = form.querySelector("button"); button.disabled = true; button.textContent = "Enviando\u2026"; status.hidden = true;
    try {
      const response = await fetch(`${apiBase()}/api/public/reserva/${encodeURIComponent(form.dataset.reservaId)}/comprobante`, { method: "POST", body: fd });
      const body = await response.json().catch(() => ({})); if (!response.ok) throw new Error(body.detail || "No se pudo enviar el comprobante.");
      form.dataset.comprobanteOk = "true"; form.querySelector('input[type="file"]').disabled = true;
      status.hidden = false; status.className = "checkout-review-note"; status.textContent = body.mensaje || "Comprobante recibido; te confirmaremos cuando revisemos el pago.";
      button.textContent = "Comprobante recibido"; maybeShowFinalStep();
    } catch (e) { status.textContent = e.message || "No se pudo enviar el comprobante."; status.hidden = false; button.disabled = false; button.textContent = "Reintentar env\u00edo"; }
  });
  if (!groupId) { error.hidden = false; error.textContent = "Falta el enlace privado del grupo. Volv\u00e9 a la propuesta y repet\u00ed la reserva."; return; }
  let cached = null; try { cached = JSON.parse(sessionStorage.getItem("tn_reserva_grupo") || "null"); } catch (_) {}
  if (cached?.grupo_estadia_id === groupId) { try { render(cached); } catch (_) {} }
  fetch(`${apiBase()}/api/public/reserva-grupo/${encodeURIComponent(groupId)}`)
    .then((r) => r.ok ? r.json() : Promise.reject(new Error("No pudimos recuperar el detalle grupal. Escribinos con tu nombre y las fechas.")))
    .then(render)
    .catch((e) => { if (!cached || cached.grupo_estadia_id !== groupId) { error.hidden = false; error.textContent = e.message || "No pudimos abrir el detalle del grupo."; } });
})();
