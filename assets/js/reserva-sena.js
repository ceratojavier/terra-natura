(function () {
  const WA_BASE = "https://wa.me/5493541571190";
  const params = new URLSearchParams(location.search);
  const reservaId = params.get("id") || "";
  const codigo = params.get("codigo") || "";
  const summary = document.getElementById("senia-resumen");
  const payment = document.getElementById("checkout-payment");
  const success = document.getElementById("checkout-success");
  const errorBox = document.getElementById("checkout-error");
  const form = document.getElementById("form-comprobante");
  const profileForm = document.getElementById("checkout-profile-form");
  const profileError = document.getElementById("checkout-profile-error");
  const fileInput = document.getElementById("archivo");
  const drop = document.getElementById("checkout-drop");
  const fileTitle = document.getElementById("checkout-file-title");
  const fileMeta = document.getElementById("checkout-file-meta");
  const uploadError = document.getElementById("checkout-upload-error");
  const bankBox = document.getElementById("senia-datos-banco");
  const bankNote = document.getElementById("checkout-bank-note");
  const mpBtn = document.getElementById("senia-mp-btn");
  const transfer = document.getElementById("transferencia-alternativa");
  const plazo = document.getElementById("senia-plazo");
  const waBtn = document.getElementById("senia-wa-btn");
  const API_FALLBACK = "https://api.alpinasterranatura.com.ar";
  let reservation = null;

  function apiBase() {
    if (["alpinasterranatura.com.ar", "www.alpinasterranatura.com.ar"].includes(location.hostname)) return API_FALLBACK;
    if (location.protocol.startsWith("http") && !location.hostname.includes("github.io")) return location.origin;
    return API_FALLBACK;
  }
  function money(n) { return new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(Number(n) || 0); }
  function esc(s) { return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
  function dateAr(s) {
    if (!s) return "—";
    const [y, m, d] = String(s).slice(0, 10).split("-");
    return y && m && d ? `${d}/${m}/${y}` : s;
  }
  function cached() {
    try { return JSON.parse(sessionStorage.getItem("tn_reserva_ok") || "null"); } catch (_) { return null; }
  }
  function bankItem(label, value, canCopy) {
    const safe = esc(value || "No informado");
    const copy = canCopy && value ? `<button type="button" class="checkout-copy" data-copy="${esc(value)}">Copiar</button>` : "";
    return `<div class="checkout-bank-item"><span>${esc(label)}</span><strong>${safe}${copy}</strong></div>`;
  }
  function renderBank(cache) {
    const dp = cache?.datos_pago || {};
    const alias = dp.alias || cache?.alias || cache?.alias_transferencia || "";
    const cuit = dp.cuit || dp.cuil || "20-28421347-6";
    const cbu = dp.cbu || dp.cbu_cvu || "";
    const banco = dp.banco || dp.medio || "";
    const titular = dp.titular || cache?.titular || "Cerato Carlos Javier";
    const concepto = dp.concepto || `Seña reserva web · ${codigo}`;
    bankBox.innerHTML = bankItem("Titular", titular, false) + bankItem("CUIT", cuit, false) + bankItem("Alias", alias, true) + bankItem("CBU / CVU", cbu, true) + bankItem("Banco / billetera", banco, false) + bankItem("Concepto", concepto, false);
    if (!cbu || !banco) {
      bankNote.hidden = false;
      bankNote.textContent = "El CBU y/o banco no están cargados en la configuración de reservas. Escribinos por WhatsApp y te pasamos los datos vigentes antes de transferir.";
    }
    bankBox.querySelectorAll("[data-copy]").forEach((btn) => btn.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(btn.dataset.copy); btn.textContent = "Copiado"; setTimeout(() => { btn.textContent = "Copiar"; }, 1400); } catch (_) {}
    }));
    if (cache?.link_mercadopago && ["mercadopago", "simulador"].includes(cache.modo_pago)) {
      mpBtn.href = cache.link_mercadopago;
      mpBtn.hidden = false;
      mpBtn.querySelector("strong").textContent = cache.modo_pago === "simulador" ? "Abrir simulador de pago" : "Pagar online con Mercado Pago";
      if (cache.modo_pago === "simulador") mpBtn.querySelector("small").textContent = "Entorno de prueba";
      if (cache.modo_pago === "mercadopago") transfer.open = false;
    }
    if (cache?.texto_plazo) plazo.textContent = cache.texto_plazo;
    else if (cache?.plazo_horas) plazo.textContent = `La pre-reserva mantiene las fechas por ${cache.plazo_horas} horas. Pasado ese plazo se liberan automáticamente.`;
    const msg = cache?.texto_whatsapp || `Hola, quiero consultar por mi reserva ${codigo} en Terra Natura.`;
    waBtn.href = WA_BASE + "?text=" + encodeURIComponent(msg);
  }
  function renderSummary(data, cache) {
    const total = data?.precio_total ?? cache?.total;
    const sena = data?.senia_referencia ?? cache?.senia;
    const unidadLabel = data?.unidad_nombre || ({ "alpina-1": "Alpina 1", "alpina-2": "Alpina 2", "alpina-3": "Alpina 3", "suite-4": "Suite 4 · Planta baja", "suite-5": "Suite 5 · Planta alta" })[data?.unidad_id] || "Alojamiento Terra Natura";
    document.getElementById("checkout-unit").textContent = unidadLabel;
    document.getElementById("checkout-dates").innerHTML = `<div class="checkout-date"><span>Ingreso</span><strong>${esc(dateAr(data?.check_in))}</strong></div><div class="checkout-date"><span>Salida</span><strong>${esc(dateAr(data?.check_out))}</strong></div>`;
    document.getElementById("checkout-summary-extra").textContent = `${cache?.personas ? `${cache.personas} huésped${cache.personas === 1 ? "" : "es"} · ` : ""}Código ${codigo}`;
    document.getElementById("checkout-total").textContent = money(total);
    document.getElementById("checkout-deposit").textContent = money(sena);
    summary.hidden = false;
  }
  function showError(message) { errorBox.textContent = message; errorBox.hidden = false; }

  if (!reservaId || !codigo) { showError("Falta el enlace de la reserva. Volvé a consultar disponibilidad desde la web."); return; }
  const cache = cached();
  renderSummary(null, cache);
  renderBank(cache);
  fetch(`${apiBase()}/api/public/reserva/${encodeURIComponent(reservaId)}/estado`)
    .then((r) => r.ok ? r.json() : Promise.reject(new Error("No pudimos cargar los datos de la reserva.")))
    .then((data) => { reservation = data; renderSummary(data, cache); payment.hidden = false; })
    .catch((err) => { payment.hidden = false; showError(err.message + " Revisá el código de reserva antes de pagar."); });

  function validateFile(file) {
    if (!file) return "Adjuntá el comprobante para continuar.";
    if (file.size > 8_000_000) return "El archivo supera el máximo de 8 MB.";
    if (!/\.(jpe?g|png|webp|pdf)$/i.test(file.name)) return "Elegí un archivo JPG, PNG, WebP o PDF.";
    return "";
  }
  function setFile(file) {
    uploadError.hidden = true;
    const problem = validateFile(file);
    if (problem) { if (file) { uploadError.textContent = problem; uploadError.hidden = false; } return; }
    fileTitle.textContent = file.name;
    fileMeta.textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB · Listo para enviar`;
  }
  fileInput.addEventListener("change", () => setFile(fileInput.files[0]));
  drop.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fileInput.click(); } });
  ["dragenter", "dragover"].forEach((name) => drop.addEventListener(name, (e) => { e.preventDefault(); drop.classList.add("is-dragging"); }));
  ["dragleave", "drop"].forEach((name) => drop.addEventListener(name, (e) => { e.preventDefault(); drop.classList.remove("is-dragging"); }));
  drop.addEventListener("drop", (e) => { const f = e.dataTransfer.files[0]; if (!f) return; try { const dt = new DataTransfer(); dt.items.add(f); fileInput.files = dt.files; } catch (_) {} setFile(f); });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    uploadError.hidden = true;
    const file = fileInput.files[0];
    const problem = validateFile(file);
    if (problem) { uploadError.textContent = problem; uploadError.hidden = false; fileInput.focus(); return; }
    const fd = new FormData();
    fd.append("codigo", codigo);
    fd.append("archivo", file);
    if (cache?.telefono) fd.append("telefono", cache.telefono);
    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    btn.innerHTML = "Enviando comprobante…";
    try {
      const response = await fetch(`${apiBase()}/api/public/reserva/${encodeURIComponent(reservaId)}/comprobante`, { method: "POST", body: fd });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.detail || "No pudimos recibir el comprobante. Probá otra vez o escribinos por WhatsApp.");
      payment.hidden = true;
      success.hidden = false;
      document.getElementById("checkout-success-code").textContent = `Código de pre-reserva ${codigo}`;
      document.querySelector(".checkout-heading").hidden = true;
      document.querySelector(".checkout-back").hidden = true;
    } catch (err) {
      uploadError.textContent = err.message || "No pudimos enviar el comprobante.";
      uploadError.hidden = false;
    } finally { btn.disabled = false; btn.innerHTML = 'Confirmar pago y enviar comprobante <span aria-hidden="true">→</span>'; }
  });

  profileForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    profileError.hidden = true;
    const data = new FormData(profileForm);
    const payload = {
      codigo,
      dni: String(data.get("dni") || "").replace(/\D/g, ""),
      domicilio: String(data.get("domicilio") || "").trim(),
      localidad: String(data.get("localidad") || "").trim(),
      provincia: String(data.get("provincia") || "").trim(),
      email: String(data.get("email") || "").trim() || null,
    };
    const btn = profileForm.querySelector("button[type=submit]");
    btn.disabled = true;
    btn.textContent = "Guardando datos…";
    try {
      const response = await fetch(`${apiBase()}/api/public/reserva/${encodeURIComponent(reservaId)}/datos-pasajero`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.detail || "No pudimos guardar los datos de la pre-reserva.");
      profileForm.hidden = true;
      document.getElementById("checkout-success-title").hidden = true;
      document.getElementById("checkout-success-description").hidden = true;
      document.getElementById("checkout-final-state").hidden = false;
      document.getElementById("checkout-success-code").textContent = `Código de pre-reserva ${codigo}`;
    } catch (err) {
      profileError.textContent = err.message || "No pudimos guardar los datos. Probá de nuevo.";
      profileError.hidden = false;
    } finally {
      btn.disabled = false;
      btn.innerHTML = 'Guardar datos y finalizar <span aria-hidden="true">→</span>';
    }
  });
})();
