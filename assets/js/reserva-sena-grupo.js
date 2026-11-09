(function () {
  const API = "https://api.alpinasterranatura.com.ar";
  function apiBase() {
    if (location.hostname === "alpinasterranatura.com.ar" || location.hostname === "www.alpinasterranatura.com.ar") return API;
    if (location.protocol.startsWith("http") && !location.hostname.includes("github.io")) return location.origin;
    return API;
  }
  const groupId = new URLSearchParams(location.search).get("grupo") || "";
  const root = document.getElementById("grupo-unidades");
  const summary = document.getElementById("grupo-resumen");
  const bank = document.getElementById("grupo-banco");
  const error = document.getElementById("grupo-error");
  const plazo = document.getElementById("grupo-plazo");

  const fmt = (n) => new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 0 }).format(Number(n) || 0);
  function el(tag, text, cls) {
    const node = document.createElement(tag);
    if (text != null) node.textContent = text;
    if (cls) node.className = cls;
    return node;
  }
  function render(data) {
    if (!data || !Array.isArray(data.reservas) || !data.reservas.length) throw new Error("No encontramos el detalle de este grupo de reservas.");
    if (data.texto_plazo) plazo.textContent = data.texto_plazo;
    else if (data.plazo_horas) plazo.textContent = `Transferí las señas dentro de las próximas ${data.plazo_horas} horas para mantener las fechas bloqueadas.`;
    summary.hidden = false;
    summary.append(el("strong", `Grupo de estadía · ${data.reservas.length} cabañas`));
    summary.append(el("p", `Total: ${fmt(data.total)} · Señas: ${fmt(data.senia_total)}`));
    const bankData = data.datos_pago || {};
    const bankLines = [
      ["Titular", bankData.titular], ["CUIL", bankData.cuil], ["Alias", bankData.alias], ["Medio", bankData.medio],
    ].filter(([, value]) => value);
    if (bankLines.length) {
      bank.hidden = false;
      bank.append(el("h2", "Transferencia"));
      bank.append(el("p", "Hacé la transferencia por separado para cada cabaña. En cada comprobante indicá el código de esa reserva."));
      bankLines.forEach(([label, value]) => bank.append(el("p", `${label}: ${value}`)));
    }
    root.replaceChildren();

    data.reservas.forEach((r) => {
      const card = el("article", null, "senia-exito-box");
      card.append(el("h2", r.unidad_nombre || r.unidad_id));
      card.append(el("p", `Titular: ${r.titular || "Titular de la reserva"}`));
      card.append(el("p", `${r.check_in} → ${r.check_out} · Código ${r.codigo}`));
      card.append(el("p", `Total de esta cabaña: ${fmt(r.total)} · Seña: ${fmt(r.senia)}`));
      if (r.link_mercadopago && ["mercadopago", "simulador"].includes(r.modo_pago)) {
        const pay = el("a", r.modo_pago === "simulador" ? "Abrir simulador de pago" : "Pagar esta seña con Mercado Pago", "btn btn-primary");
        pay.href = r.link_mercadopago;
        pay.target = "_blank";
        pay.rel = "noopener noreferrer";
        card.append(pay);
      }
      const form = document.createElement("form");
      form.dataset.reservaId = r.reserva_id;
      form.dataset.codigo = r.codigo;
      const label = el("label", "Comprobante de esta cabaña (JPG, PNG o PDF)");
      const file = document.createElement("input");
      file.type = "file";
      file.accept = "image/*,.pdf";
      file.required = true;
      label.append(file);
      const submit = el("button", "Enviar comprobante", "btn btn-outline");
      submit.type = "submit";
      form.append(label, submit);
      const status = el("p", "", "result");
      status.hidden = true;
      form.append(status);
      card.append(form);
      root.append(card);
    });
  }

  root.addEventListener("submit", async (event) => {
    const form = event.target.closest("form[data-reserva-id]");
    if (!form) return;
    event.preventDefault();
    const file = form.querySelector('input[type="file"]').files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("codigo", form.dataset.codigo);
    fd.append("archivo", file);
    const button = form.querySelector("button");
    const status = form.querySelector(".result");
    button.disabled = true;
    button.textContent = "Enviando…";
    try {
      const response = await fetch(`${apiBase()}/api/public/reserva/${encodeURIComponent(form.dataset.reservaId)}/comprobante`, { method: "POST", body: fd });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || "No se pudo enviar el comprobante.");
      status.hidden = false;
      status.className = "result ok";
      status.textContent = body.mensaje || "Comprobante recibido; te confirmaremos cuando revisemos el pago.";
      form.reset();
    } catch (e) {
      status.hidden = false;
      status.className = "result err";
      status.textContent = e.message || "No se pudo enviar el comprobante.";
    }
    button.disabled = false;
    button.textContent = "Enviar comprobante";
  });

  if (!groupId) {
    error.hidden = false;
    error.textContent = "Falta el enlace privado del grupo. Volvé a la web y repetí la reserva.";
    return;
  }
  let cached = null;
  try { cached = JSON.parse(sessionStorage.getItem("tn_reserva_grupo") || "null"); } catch (_) {}
  if (cached?.grupo_estadia_id === groupId) {
    try { render(cached); return; } catch (_) {}
  }
  fetch(`${apiBase()}/api/public/reserva-grupo/${encodeURIComponent(groupId)}`)
    .then((r) => r.ok ? r.json() : Promise.reject(new Error("No pudimos recuperar la reserva grupal. Escribinos por WhatsApp con tu nombre y las fechas.")))
    .then(render)
    .catch((e) => { error.hidden = false; error.textContent = e.message || "No pudimos abrir el detalle del grupo."; });
})();
