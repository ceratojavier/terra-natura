/**
 * Pipeline marketing + cola de aprobación — /programa
 */
(function () {
  var CANAL_LABEL = {
    instagram: "Instagram",
    facebook: "Facebook",
    whatsapp_status: "WA Status",
    tiktok: "TikTok",
  };

  var ESTADO_BADGE = {
    borrador: "badge-muted",
    pendiente_aprobacion: "badge-warn",
    aprobado: "badge-ok",
    publicado: "badge-done",
    cancelado: "badge-muted",
  };

  function esc(s) {
    if (!s) return "";
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function fetchJson(url, opts) {
    return fetch(url, opts).then(function (r) {
      if (!r.ok) return r.text().then(function (t) {
        throw new Error(t || r.statusText);
      });
      return r.json();
    });
  }

  function renderPlan(plan) {
    var panel = document.getElementById("panel-plan-dia");
    if (!panel || !plan) return;
    var ev = plan.evento;
    panel.innerHTML =
      '<div class="tn-plan-grid">' +
      '<div class="tn-plan-meta">' +
      '<span class="tn-badge">' + esc(plan.objetivo) + "</span>" +
      '<span class="tn-badge tn-badge-soft">' + esc(plan.angulo) + "</span>" +
      "</div>" +
      "<h3>" + esc(plan.titulo || "Sin título") + "</h3>" +
      '<p class="tn-plan-razon">' + esc(plan.razon || "") + "</p>" +
      (ev && ev.nombre
        ? '<p class="tn-plan-evento">Contexto: ' + esc(ev.nombre) + "</p>"
        : "") +
      '<p class="tn-plan-copy-preview">' + esc((plan.copy || "").slice(0, 220)) + "…</p>" +
      "</div>";
  }

  function cargarPlanDia() {
    return fetchJson("/api/ama/estratega/plan")
      .then(function (d) {
        renderPlan(d.plan);
      })
      .catch(function () {
        var panel = document.getElementById("panel-plan-dia");
        if (panel) {
          panel.innerHTML =
            '<p class="cotiza-muted">No se pudo cargar el plan. Verificá que el servidor esté encendido.</p>';
        }
      });
  }

  function pubPorId(pubId) {
    return fetchJson("/api/ama/calendario").then(function (d) {
      var rows = d.publicaciones || [];
      for (var i = 0; i < rows.length; i++) {
        if (rows[i].id === pubId) return rows[i];
      }
      return null;
    });
  }

  function cargarCola() {
    var tbody = document.getElementById("tabla-cola-body");
    if (!tbody) return Promise.resolve();

    return Promise.all([
      fetchJson("/api/ama/publish/cola"),
      fetchJson("/api/ama/calendario"),
    ])
      .then(function (res) {
        var cola = res[0].items || [];
        var pubs = res[1].publicaciones || [];
        var byId = {};
        pubs.forEach(function (p) {
          byId[p.id] = p;
        });

        var rows = cola.length ? cola : pubs.filter(function (p) {
          return ["pendiente_aprobacion", "aprobado", "borrador"].indexOf(p.estado) >= 0;
        }).map(function (p) {
          return {
            pub_id: p.id,
            canal: p.canal,
            estado: p.estado,
            video_ruta: p.video_ruta,
            copy_preview: (p.copy || "").slice(0, 80),
          };
        });

        if (!rows.length) {
          tbody.innerHTML =
            '<tr><td colspan="6" class="tn-empty">No hay piezas en cola. Ejecutá el pipeline del día.</td></tr>';
          var statCola = document.getElementById("stat-cola");
          if (statCola) statCola.textContent = "0";
          return;
        }

        tbody.innerHTML = "";
        rows.forEach(function (item) {
          var pub = byId[item.pub_id] || {};
          var estado = item.estado || pub.estado || "borrador";
          var badge = ESTADO_BADGE[estado] || "badge-muted";
          var tr = document.createElement("tr");
          tr.innerHTML =
            "<td>" + esc(pub.fecha_publicacion || "—") + "</td>" +
            "<td>" + esc(CANAL_LABEL[item.canal || pub.canal] || item.canal) + "</td>" +
            "<td>" + esc(pub.titulo || item.copy_preview || "—") + "</td>" +
            '<td><span class="tn-pill ' + badge + '">' + esc(estado.replace(/_/g, " ")) + "</span></td>" +
            "<td>" + (pub.video_ruta || item.video_ruta ? "✓" : "—") + "</td>" +
            '<td class="tn-actions"></td>';
          var actions = tr.querySelector(".tn-actions");

          if (estado === "pendiente_aprobacion" || estado === "borrador") {
            var btnOk = document.createElement("button");
            btnOk.type = "button";
            btnOk.className = "btn btn-primary btn-sm";
            btnOk.textContent = "Aprobar";
            btnOk.addEventListener("click", function () {
              aprobar(item.pub_id, btnOk);
            });
            actions.appendChild(btnOk);
          }

          if (pub.video_ruta) {
            var btnVid = document.createElement("a");
            btnVid.className = "btn btn-outline btn-sm";
            btnVid.textContent = "Video";
            btnVid.href =
              "/api/ama/video/archivo?ruta=" + encodeURIComponent(pub.video_ruta);
            btnVid.target = "_blank";
            actions.appendChild(btnVid);
          }

          var btnMkt = document.createElement("a");
          btnMkt.className = "btn btn-outline btn-sm";
          btnMkt.href = "/marketing";
          btnMkt.textContent = "Editar";
          actions.appendChild(btnMkt);

          tbody.appendChild(tr);
        });

        var statCola = document.getElementById("stat-cola");
        if (statCola) {
          var pend = rows.filter(function (r) {
            return r.estado === "pendiente_aprobacion";
          }).length;
          statCola.textContent = String(pend || rows.length);
        }
      })
      .catch(function () {
        tbody.innerHTML =
          '<tr><td colspan="6" class="tn-empty">Error al cargar cola. ¿Servidor encendido?</td></tr>';
      });
  }

  function aprobar(pubId, btn) {
    if (btn) {
      btn.disabled = true;
      btn.textContent = "…";
    }
    fetchJson("/api/ama/publish/aprobar/" + encodeURIComponent(pubId), { method: "POST" })
      .then(function () {
        return cargarCola();
      })
      .then(function () {
        if (typeof window.cargarHoy === "function") window.cargarHoy();
      })
      .catch(function (e) {
        alert("No se pudo aprobar: " + e.message);
      })
      .finally(function () {
        if (btn) {
          btn.disabled = false;
          btn.textContent = "Aprobar";
        }
      });
  }

  function ejecutarPipeline() {
    var btn = document.getElementById("btn-pipeline-dia");
    var logWrap = document.getElementById("panel-pipeline-log");
    var logPre = document.getElementById("pipeline-log-text");
    if (
      !confirm(
        "¿Ejecutar pipeline de hoy?\n\nPlan → guion → video (MoviePy) → brief CapCut → cola.\nPuede tardar varios minutos si genera video."
      )
    ) {
      return;
    }
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Procesando…";
    }
    if (logWrap) logWrap.hidden = false;
    if (logPre) logPre.textContent = "Iniciando pipeline…\n";

    fetchJson("/api/ama/video/pipeline/dia", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        render_video: true,
        guardar_calendario: true,
        carpeta_media: "Parque",
      }),
    })
      .then(function (r) {
        if (logPre) {
          logPre.textContent = JSON.stringify(r, null, 2);
        }
        alert(
          (r.ok ? "Pipeline OK" : "Pipeline con avisos") +
            "\nCarpeta: " +
            (r.carpeta || "") +
            (r.video && r.video.ruta ? "\nVideo: " + r.video.ruta : "")
        );
        return Promise.all([cargarPlanDia(), cargarCola(), cargarPlanDia()]);
      })
      .then(function () {
        if (typeof window.cargarHoy === "function") window.cargarHoy();
        var cargarEstado = window.cargarEstadoPrograma;
        if (typeof cargarEstado === "function") cargarEstado();
      })
      .catch(function (e) {
        if (logPre) logPre.textContent += "\nError: " + e.message;
        alert("Error en pipeline: " + e.message);
      })
      .finally(function () {
        if (btn) {
          btn.disabled = false;
          btn.textContent = "Ejecutar pipeline de hoy";
        }
      });
  }

  var btnPipe = document.getElementById("btn-pipeline-dia");
  if (btnPipe) btnPipe.addEventListener("click", ejecutarPipeline);

  var btnRef = document.getElementById("btn-refrescar-cola");
  if (btnRef) btnRef.addEventListener("click", function () {
    cargarCola();
    cargarPlanDia();
  });

  cargarPlanDia();
  cargarCola();

  window.TNMarketing = {
    recargarCola: cargarCola,
    recargarPlan: cargarPlanDia,
  };
})();
