const API = "";

async function getJson(url, opts = {}) {
  const r = await fetch(API + url, opts);
  if (!r.ok) throw new Error((await r.text()) || r.statusText);
  return r.json();
}

function el(html) {
  const d = document.createElement("div");
  d.innerHTML = html.trim();
  return d.firstChild;
}

function esc(s) {
  if (!s) return "";
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

const CANAL_LABEL = {
  instagram: "Instagram",
  facebook: "Facebook",
  whatsapp_status: "WA Status",
  tiktok: "TikTok",
};

function renderStats(hub) {
  const box = document.getElementById("hub-stats");
  if (!box) return;
  const pend =
    hub.cola_pendientes != null ? hub.cola_pendientes : "—";
  box.innerHTML = `
    <div class="hub-stat-line"><span>Leads CRM</span><strong>${hub.leads_total}</strong></div>
    <div class="hub-stat-line"><span>Reservas activas</span><strong>${hub.reservas_activas}</strong></div>
    <div class="hub-stat-line"><span>Agentes</span><strong>${hub.agentes?.length || 0}</strong></div>
    <div class="hub-stat-line"><span>Cola pendiente</span><strong>${pend}</strong></div>
  `;
}

function renderAgentCard(meta) {
  const card = el(`
    <article class="agent-card" data-id="${meta.id}">
      <header class="agent-card-head">
        <span class="agent-icon">${meta.icono}</span>
        <h3>${esc(meta.nombre)}</h3>
      </header>
      <p class="desc">${esc(meta.descripcion)}</p>
      <ul class="agent-tasks">${meta.tareas
        .map((t) => `<li>${esc(t.titulo)}</li>`)
        .join("")}</ul>
      <div class="agent-card-actions">
        <button type="button" class="btn btn-outline btn-sm btn-run">Ejecutar</button>
        ${
          meta.id === "productor"
            ? '<button type="button" class="btn btn-primary btn-sm btn-pipeline">Pipeline hoy</button>'
            : ""
        }
      </div>
      <div class="agent-result hidden"></div>
    </article>
  `);

  const run = async (taskIds) => {
    const resBox = card.querySelector(".agent-result");
    resBox.classList.remove("hidden");
    resBox.innerHTML = '<p class="tarea">Ejecutando…</p>';
    try {
      const body = taskIds ? JSON.stringify({ task_ids: taskIds }) : "{}";
      const data = await getJson(`/api/agentes/${meta.id}/ejecutar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
      });
      let html = `<p class="status ${data.status}">${data.status.toUpperCase()}</p>`;
      for (const a of data.alertas || []) {
        html += `<p class="alerta">⚠ ${esc(a)}</p>`;
      }
      for (const t of data.tareas || []) {
        html += `<p class="tarea">${t.ok ? "✓" : "✗"} <strong>${esc(
          t.task_id
        )}</strong>: ${esc(t.mensaje)}</p>`;
      }
      resBox.innerHTML = html;
      if (meta.id === "productor" || meta.id === "distribuidor") {
        await cargarCola();
      }
    } catch (e) {
      resBox.innerHTML = `<p class="status err">${esc(e.message)}</p>`;
    }
  };

  card.querySelector(".btn-run").onclick = () => run(null);
  const btnPipe = card.querySelector(".btn-pipeline");
  if (btnPipe) {
    btnPipe.onclick = () => run(["pipeline_dia"]);
  }
  return card;
}

async function cargarCola() {
  const tbody = document.getElementById("tabla-cola-agentes");
  if (!tbody) return;
  try {
    const [colaRes, calRes] = await Promise.all([
      getJson("/api/ama/publish/cola"),
      getJson("/api/ama/calendario"),
    ]);
    const pubs = calRes.publicaciones || [];
    const byId = Object.fromEntries(pubs.map((p) => [p.id, p]));
    let items = colaRes.items || [];
    if (!items.length) {
      items = pubs
        .filter((p) =>
          ["pendiente_aprobacion", "aprobado", "borrador"].includes(p.estado)
        )
        .slice(0, 12)
        .map((p) => ({
          pub_id: p.id,
          canal: p.canal,
          estado: p.estado,
          copy_preview: (p.copy || "").slice(0, 100),
        }));
    }
    if (!items.length) {
      tbody.innerHTML =
        '<tr><td colspan="4" class="tn-empty">Cola vacía. Ejecutá el pipeline.</td></tr>';
      return;
    }
    tbody.innerHTML = "";
    for (const item of items.slice(0, 15)) {
      const pub = byId[item.pub_id] || {};
      const tr = document.createElement("tr");
      const estado = item.estado || pub.estado;
      tr.innerHTML = `
        <td>${esc(CANAL_LABEL[item.canal || pub.canal] || item.canal)}</td>
        <td><span class="tn-pill badge-warn">${esc(estado)}</span></td>
        <td>${esc(pub.titulo || item.copy_preview || "—")}</td>
        <td class="tn-actions"></td>
      `;
      const actions = tr.querySelector(".tn-actions");
      if (estado === "pendiente_aprobacion" || estado === "borrador") {
        const btn = document.createElement("button");
        btn.className = "btn btn-primary btn-sm";
        btn.textContent = "Aprobar";
        btn.onclick = async () => {
          btn.disabled = true;
          try {
            await getJson(
              `/api/ama/publish/aprobar/${encodeURIComponent(item.pub_id)}`,
              { method: "POST" }
            );
            await cargarCola();
            await loadHub();
          } catch (e) {
            alert(e.message);
          } finally {
            btn.disabled = false;
          }
        };
        actions.appendChild(btn);
      }
      const link = document.createElement("a");
      link.href = "/programa#seccion-cola";
      link.className = "btn btn-outline btn-sm";
      link.textContent = "Ver";
      actions.appendChild(link);
      tbody.appendChild(tr);
    }
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4" class="tn-empty">${esc(
      e.message
    )}</td></tr>`;
  }
}

async function loadHub() {
  const hub = await getJson("/api/agentes/hub");
  const pill = document.getElementById("agentes-estado");
  if (pill) {
    pill.textContent = "Servidor activo";
    pill.style.background = "rgba(46, 203, 149, 0.2)";
  }
  renderStats(hub);
  const grid = document.getElementById("agentes-grid");
  grid.innerHTML = "";
  for (const a of hub.agentes) {
    grid.appendChild(renderAgentCard(a));
  }
  if (hub.ultimo_ciclo) {
    document.getElementById("ultimo-ciclo").classList.remove("hidden");
    document.getElementById("ciclo-json").textContent = JSON.stringify(
      hub.ultimo_ciclo,
      null,
      2
    );
  }
  await cargarCola();
}

async function ejecutarPipeline() {
  const btn = document.getElementById("btn-pipeline-agentes");
  const st = document.getElementById("ciclo-status");
  if (
    !confirm(
      "¿Ejecutar pipeline completo de hoy? (estratega + guion + video + cola)"
    )
  ) {
    return;
  }
  btn.disabled = true;
  st.textContent = "Pipeline…";
  st.className = "tn-pill badge-warn";
  try {
    const data = await getJson("/api/ama/video/pipeline/dia", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        render_video: true,
        guardar_calendario: true,
      }),
    });
    st.textContent = data.ok ? "Pipeline OK" : "Con avisos";
    st.className = data.ok ? "tn-pill badge-ok" : "tn-pill badge-warn";
    alert(
      `Pipeline ${data.fecha}\nCarpeta: ${data.carpeta || ""}\n${
        data.publicacion_id ? "ID: " + data.publicacion_id : ""
      }`
    );
    await loadHub();
  } catch (e) {
    st.textContent = "Error";
    st.className = "tn-pill badge-danger";
    alert(e.message);
  } finally {
    btn.disabled = false;
  }
}

document.getElementById("btn-ciclo").onclick = async () => {
  const btn = document.getElementById("btn-ciclo");
  const st = document.getElementById("ciclo-status");
  btn.disabled = true;
  st.textContent = "Ciclo en curso…";
  st.className = "tn-pill badge-warn";
  try {
    const data = await getJson("/api/agentes/ciclo-diario", { method: "POST" });
    st.textContent = data.ok ? "Ciclo OK" : "Con alertas";
    st.className = data.ok ? "tn-pill badge-ok" : "tn-pill badge-warn";
    document.getElementById("ultimo-ciclo").classList.remove("hidden");
    document.getElementById("ciclo-json").textContent = JSON.stringify(
      data,
      null,
      2
    );
    await loadHub();
  } catch (e) {
    st.textContent = e.message;
    st.className = "tn-pill badge-danger";
  } finally {
    btn.disabled = false;
  }
};

document.getElementById("btn-pipeline-agentes").onclick = ejecutarPipeline;
document.getElementById("btn-refrescar-cola-agentes").onclick = () => {
  cargarCola();
  loadHub();
};

loadHub().catch((e) => {
  const pill = document.getElementById("agentes-estado");
  if (pill) {
    pill.textContent = "Servidor apagado";
    pill.style.background = "rgba(255, 109, 127, 0.25)";
  }
  document.getElementById("hub-stats").innerHTML = `<p class="tn-empty">${esc(
    e.message
  )}. Abrí Terra Natura desde el escritorio.</p>`;
});
