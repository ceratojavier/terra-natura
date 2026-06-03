(function () {
  var siteConfig = { apiBase: "" };

  function apiBase() {
    var b = (siteConfig.apiBase || "").trim().replace(/\/$/, "");
    if (b) return b;
    if (location.protocol.startsWith("http") && !location.hostname.includes("github.io")) {
      return location.origin;
    }
    return "";
  }

  function apiFetch(path, options) {
    var base = apiBase();
    if (!base) {
      return Promise.reject(new Error("sin_api"));
    }
    return fetch(base + path, options || {}).then(function (r) {
      if (!r.ok) {
        var err = new Error("HTTP " + r.status);
        err.status = r.status;
        return r.json().catch(function () {
          throw err;
        }).then(function (body) {
          err.body = body;
          throw err;
        });
      }
      return r.json();
    });
  }

  function apiUrl(path) {
    var base = apiBase();
    return base ? base + path : path;
  }

  function mensajeSinServidor(el) {
    if (!el) return;
    el.textContent =
      "El panel necesita el programa Terra Natura encendido (servidor). En tu PC: abrí local/inicia_servidor_interno.bat y entrá a http://localhost:8000/panel — En internet: configurá apiBase en assets/data/site-config.json con la URL del servidor.";
  }

  function cargarSiteConfig() {
    return fetch("./assets/data/site-config.json")
      .then(function (r) {
        return r.ok ? r.json() : {};
      })
      .then(function (j) {
        siteConfig = Object.assign(siteConfig, j || {});
      })
      .catch(function () {});
  }

  function showPane(name) {
    document.querySelectorAll("[data-pane]").forEach(function (el) {
      el.hidden = el.getAttribute("data-pane") !== name;
    });
  }

  document.querySelectorAll("[data-show-pane]").forEach(function (el) {
    el.addEventListener("click", function () {
      var target = el.getAttribute("data-show-pane");
      showPane(target || "menu");

      if (target === "calendario") {
        cargarCalendario();
      }
      if (target === "tarifas") {
        cargarTarifasCalendario();
      }
      if (target === "reservas") {
        cargarReservas();
      }
      if (target === "nueva-reserva") {
        initNuevaReserva();
      }
      if (target === "ical") {
        cargarEnlacesIcal();
      }
    });
  });

  window.addEventListener("hashchange", function () {
    if (window.location.hash === "#/reservas") {
      showPane("reservas");
      cargarReservas();
    }
    if (window.location.hash === "#/nueva-reserva") {
      showPane("nueva-reserva");
      initNuevaReserva();
    }
  });

  if (window.location.hash === "#/reservas") {
    showPane("reservas");
    cargarReservas();
  }
  if (window.location.hash === "#/tarifas") {
    showPane("tarifas");
  }
  if (window.location.hash === "#/ical") {
    showPane("ical");
    cargarEnlacesIcal();
  }
  if (window.location.hash === "#/calendario") {
    showPane("calendario");
    cargarCalendario();
  }
  if (window.location.hash === "#/nueva-reserva") {
    showPane("nueva-reserva");
  }

  function ymdISO(d) {
    var y = d.getFullYear();
    var m = String(d.getMonth() + 1).padStart(2, "0");
    var day = String(d.getDate()).padStart(2, "0");
    return y + "-" + m + "-" + day;
  }

  function fmtFechaISO(s) {
    if (!s) return "";
    var d = new Date(s + "T12:00:00");
    return d.toLocaleDateString("es-AR");
  }

  function fmtMoney(n, moneda) {
    var code = moneda === "USD" ? "USD" : "ARS";
    return new Intl.NumberFormat("es-AR", {
      style: "currency",
      currency: code,
      maximumFractionDigits: 0,
    }).format(n || 0);
  }

  function codigoReserva(id) {
    if (!id) return "—";
    return "TN-" + String(id).replace(/-/g, "").slice(0, 8).toUpperCase();
  }

  var tb = document.getElementById("tabla-reservas-body");
  var msgReservas = document.getElementById("msg-reservas");
  var desdeEl = document.getElementById("panel-desde");
  var hastaEl = document.getElementById("panel-hasta");

  if (desdeEl && hastaEl && !desdeEl.value) {
    var hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    var fin = new Date(hoy.getTime());
    fin.setMonth(fin.getMonth() + 4);
    desdeEl.value = ymdISO(hoy);
    hastaEl.value = ymdISO(fin);
  }

  window.recargarReservas = function () {
    cargarReservas();
  };

  function cargarReservas() {
    if (!tb || !msgReservas || !desdeEl || !hastaEl) return;
    tb.innerHTML = "";
    msgReservas.textContent = "Cargando…";

    var u = {};

    apiFetch("/api/unidades")
      .then(function (json) {
        (json.unidades || []).forEach(function (x) {
          u[x.id] = x.nombre;
        });

        var url =
          "/api/reservas?desde=" +
          encodeURIComponent(desdeEl.value) +
          "&hasta=" +
          encodeURIComponent(hastaEl.value);

        return apiFetch(url).then(function (lista) {
          return { lista: lista, unitNames: u };
        });
      })
      .then(function (pair) {
        msgReservas.textContent =
          pair.lista.length === 0
            ? "No hay reservas registradas en este rango (o base vacía)."
            : pair.lista.length + " reserva(s).";

        pair.lista
          .sort(function (a, b) {
            return (b.check_in || "").localeCompare(a.check_in || "");
          })
          .forEach(function (r) {
            var tr = document.createElement("tr");
            var un =
              pair.unitNames[r.unidad_id] || r.unidad_id;

            [
              codigoReserva(r.id),
              fmtFechaISO(r.check_in),
              fmtFechaISO(r.check_out),
              un,
              r.estado,
              r.origen || "—",
              r.huesped_nombre || "—",
              fmtMoney(r.precio_total, r.moneda),
            ].forEach(function (txt) {
              var td = document.createElement("td");
              td.textContent = txt;
              tr.appendChild(td);
            });
            tb.appendChild(tr);
          });
      })
      .catch(function (err) {
        if (err && err.message === "sin_api") {
          mensajeSinServidor(msgReservas);
        } else {
          msgReservas.textContent =
            "No se pudo cargar. ¿Tenés el servidor encendido? Probá http://localhost:8000/panel";
        }
      });
  }

  var msgCal = document.getElementById("msg-calendario");
  var calGrid = document.getElementById("calendario-grid");
  var btnSyncBooking = document.getElementById("btn-sync-booking");
  var btnSyncBookingIcal = document.getElementById("btn-sync-booking-ical");
  var btnRecargarCal = document.getElementById("btn-recargar-cal");
  var msgSyncIcal = document.getElementById("msg-sync-ical");

  function sincronizarBooking(btn, msgEl) {
    if (!apiBase()) {
      mensajeSinServidor(msgEl || msgCal);
      return;
    }
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Sincronizando…";
    }
    if (msgEl) msgEl.textContent = "Descargando calendarios de Booking…";

    apiFetch("/api/canales/sync-ical", { method: "POST" })
      .then(function (j) {
        var c = 0;
        var a = 0;
        var o = 0;
        (j.detalle || []).forEach(function (d) {
          c += d.creadas || 0;
          a += d.actualizadas || 0;
          o += d.omitidas || 0;
        });
        var txt =
          (j.mensaje ? j.mensaje + " — " : "Booking sincronizado. ") +
          "Nuevas: " +
          (j.nuevas_total || c) +
          " · Actualizadas: " +
          a +
          " · Omitidas: " +
          o;
        if (j.nuevas_total > 0) {
          txt += " — Revisá alertas arriba.";
        }
        if (msgEl) msgEl.textContent = txt;
        if (msgCal) msgCal.textContent = txt;
        cargarCalendario();
        if (tb) cargarReservas();
        cargarAlertas();
      })
      .catch(function (err) {
        var t = "Error al sincronizar.";
        if (err && err.message === "sin_api") mensajeSinServidor(msgEl || msgCal);
        else if (msgEl || msgCal) (msgEl || msgCal).textContent = t;
      })
      .finally(function () {
        if (btn) {
          btn.disabled = false;
          btn.textContent = "Sincronizar Booking ahora";
        }
      });
  }

  if (btnSyncBooking) {
    btnSyncBooking.addEventListener("click", function () {
      sincronizarBooking(btnSyncBooking, msgCal);
    });
  }
  if (btnSyncBookingIcal) {
    btnSyncBookingIcal.addEventListener("click", function () {
      sincronizarBooking(btnSyncBookingIcal, msgSyncIcal);
    });
  }
  if (btnRecargarCal) {
    btnRecargarCal.addEventListener("click", cargarCalendario);
  }

  function cargarCalendario() {
    if (!calGrid || !msgCal) return;
    calGrid.innerHTML = "";
    msgCal.textContent = "Cargando calendario…";

    if (!apiBase()) {
      mensajeSinServidor(msgCal);
      return;
    }

    var hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    var fin = new Date(hoy.getTime());
    fin.setDate(fin.getDate() + 27);
    var desde = ymdISO(hoy);
    var hasta = ymdISO(fin);

    apiFetch("/api/unidades?solo_alquilables=true")
      .then(function (json) {
        var units = json.unidades || [];
        if (!units.length) {
          msgCal.textContent = "No hay unidades configuradas.";
          return;
        }

        var promises = units.map(function (u) {
          return apiFetch(
            "/api/disponibilidad?desde=" +
              encodeURIComponent(desde) +
              "&hasta=" +
              encodeURIComponent(hasta) +
              "&unidad_id=" +
              encodeURIComponent(u.id)
          ).then(function (disp) {
            return { unidad: u, dias: disp.dias || [] };
          });
        });

        return Promise.all(promises);
      })
      .then(function (rows) {
        if (!rows) return;
        msgCal.textContent = "Próximas 4 semanas · " + rows[0].dias.length + " noches";

        var fechas = rows[0].dias.map(function (d) {
          return d.fecha;
        });

        var table = document.createElement("table");
        table.className = "calendario-table";

        var thead = document.createElement("thead");
        var hr = document.createElement("tr");
        var th0 = document.createElement("th");
        th0.textContent = "Unidad";
        hr.appendChild(th0);
        fechas.forEach(function (f) {
          var th = document.createElement("th");
          var p = f.split("-");
          th.textContent = p[2] + "/" + p[1];
          th.title = f;
          hr.appendChild(th);
        });
        thead.appendChild(hr);
        table.appendChild(thead);

        var tbody = document.createElement("tbody");
        rows.forEach(function (row) {
          var tr = document.createElement("tr");
          var tdName = document.createElement("th");
          tdName.textContent = row.unidad.nombre;
          tr.appendChild(tdName);

          var mapa = {};
          row.dias.forEach(function (d) {
            mapa[d.fecha] = d.disponible;
          });

          fechas.forEach(function (f) {
            var td = document.createElement("td");
            var libre = mapa[f] === true;
            td.className = libre ? "cal-libre" : "cal-ocupado";
            td.setAttribute("aria-label", libre ? "Libre" : "Ocupado");
            tr.appendChild(td);
          });
          tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        calGrid.appendChild(table);
      })
      .catch(function (err) {
        if (err && err.message === "sin_api") mensajeSinServidor(msgCal);
        else msgCal.textContent = "No se pudo cargar el calendario.";
      });
  }

  // --- Calendario de tarifas (lectura/edición manual por fecha) ---
  var tarifasMes = document.getElementById("tarifas-mes");
  var tarifasGrid = document.getElementById("tarifas-grid");
  var msgTarifas = document.getElementById("msg-tarifas");
  var btnCargarTarifas = document.getElementById("btn-cargar-tarifas");
  var btnGuardarTarifas = document.getElementById("btn-guardar-tarifas");

  if (tarifasMes && !tarifasMes.value) {
    var hoyTar = new Date();
    tarifasMes.value = hoyTar.toISOString().slice(0, 7);
  }

  function mesRango(ym) {
    var p = (ym || "").split("-");
    var y = Number(p[0] || 0);
    var m = Number(p[1] || 0);
    if (!y || !m) return null;
    var desde = new Date(y, m - 1, 1);
    var hasta = new Date(y, m, 0);
    return { desde: ymdISO(desde), hasta: ymdISO(hasta) };
  }

  function cargarTarifasCalendario() {
    if (!tarifasMes || !tarifasGrid || !msgTarifas) return;
    tarifasGrid.innerHTML = "";
    var r = mesRango(tarifasMes.value);
    if (!r) {
      msgTarifas.textContent = "Elegí un mes válido.";
      return;
    }
    msgTarifas.textContent = "Cargando precios del mes…";
    apiFetch(
      "/api/config/tarifas/calendario?desde=" +
        encodeURIComponent(r.desde) +
        "&hasta=" +
        encodeURIComponent(r.hasta)
    )
      .then(function (j) {
        var units = j.unidades || [];
        if (!units.length) {
          msgTarifas.textContent = "No hay unidades disponibles.";
          return;
        }
        var fechas = units[0].dias.map(function (d) {
          return d.fecha;
        });

        var table = document.createElement("table");
        table.className = "calendario-table tarifas-table";

        var thead = document.createElement("thead");
        var trh = document.createElement("tr");
        var th0 = document.createElement("th");
        th0.textContent = "Unidad";
        trh.appendChild(th0);
        fechas.forEach(function (f) {
          var th = document.createElement("th");
          th.textContent = f.slice(8, 10);
          th.title = f;
          trh.appendChild(th);
        });
        thead.appendChild(trh);
        table.appendChild(thead);

        var tbody = document.createElement("tbody");
        units.forEach(function (u) {
          var tr = document.createElement("tr");
          var thn = document.createElement("th");
          thn.textContent = u.unidad_nombre;
          tr.appendChild(thn);
          (u.dias || []).forEach(function (d) {
            var td = document.createElement("td");
            td.className = d.disponible ? "cal-libre" : "cal-ocupado";
            var inp = document.createElement("input");
            inp.type = "number";
            inp.min = "1";
            inp.step = "1";
            inp.value = String(Math.round(d.precio_noche_ars || 0));
            inp.className = "tarifa-input";
            inp.setAttribute("data-unidad", u.unidad_id);
            inp.setAttribute("data-fecha", d.fecha);
            inp.title =
              (d.disponible ? "Libre" : "Ocupado") +
              " · " +
              (d.temporada || "") +
              " · infl. " +
              (d.coeficiente_inflacion_pct || 0) +
              "%";
            td.appendChild(inp);
            tr.appendChild(td);
          });
          tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        tarifasGrid.appendChild(table);
        msgTarifas.textContent =
          "Editá un precio y tocá Guardar cambios. Si querés volver al automático, borrá el valor y guardá.";
      })
      .catch(function (err) {
        if (err && err.message === "sin_api") mensajeSinServidor(msgTarifas);
        else msgTarifas.textContent = "No se pudo cargar el calendario de tarifas.";
      });
  }

  function guardarTarifasCambios() {
    if (!tarifasGrid || !msgTarifas) return;
    var inputs = Array.from(tarifasGrid.querySelectorAll(".tarifa-input"));
    if (!inputs.length) {
      msgTarifas.textContent = "Primero cargá el calendario del mes.";
      return;
    }
    msgTarifas.textContent = "Guardando cambios…";
    var reqs = inputs.map(function (inp) {
      var val = inp.value.trim();
      return apiFetch("/api/config/tarifas/override", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          unidad_id: inp.getAttribute("data-unidad"),
          fecha: inp.getAttribute("data-fecha"),
          precio_noche_ars: val ? Number(val) : null,
          motivo: "Ajuste manual desde panel dueño",
        }),
      });
    });
    Promise.all(reqs)
      .then(function () {
        msgTarifas.textContent = "Tarifas guardadas. Refrescando calendario…";
        cargarTarifasCalendario();
      })
      .catch(function (err) {
        if (err && err.message === "sin_api") mensajeSinServidor(msgTarifas);
        else msgTarifas.textContent = "No se pudieron guardar algunos cambios.";
      });
  }

  if (btnCargarTarifas) btnCargarTarifas.addEventListener("click", cargarTarifasCalendario);
  if (btnGuardarTarifas) btnGuardarTarifas.addEventListener("click", guardarTarifasCambios);

  // --- Nueva reserva (operación móvil) ---
  var nrForm = document.getElementById("form-nueva-reserva");
  var nrExito = document.getElementById("nr-exito");
  var nrUnidad = document.getElementById("nr-unidad");
  var nrCheckin = document.getElementById("nr-checkin");
  var nrCheckout = document.getElementById("nr-checkout");
  var nrCotizacion = document.getElementById("nr-cotizacion");
  var msgNueva = document.getElementById("msg-nueva-reserva");
  var nrUnidadesCargadas = false;

  function resetNuevaReserva() {
    if (nrForm) nrForm.hidden = false;
    if (nrExito) nrExito.hidden = true;
    if (msgNueva) msgNueva.textContent = "";
    if (nrCotizacion) {
      nrCotizacion.hidden = true;
      nrCotizacion.textContent = "";
    }
  }

  function initNuevaReserva() {
    resetNuevaReserva();
    if (!nrUnidad || !nrCheckin || !nrCheckout) return;

    var hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    if (!nrCheckin.value) {
      nrCheckin.value = ymdISO(hoy);
      var out = new Date(hoy.getTime());
      out.setDate(out.getDate() + 2);
      nrCheckout.value = ymdISO(out);
    }

    if (nrUnidadesCargadas) return;

    if (!apiBase()) {
      mensajeSinServidor(msgNueva);
      return;
    }

    apiFetch("/api/unidades?solo_alquilables=true")
      .then(function (json) {
        nrUnidad.innerHTML = "";
        (json.unidades || []).forEach(function (u) {
          var opt = document.createElement("option");
          opt.value = u.id;
          opt.textContent = u.nombre;
          nrUnidad.appendChild(opt);
        });
        nrUnidadesCargadas = true;
      })
      .catch(function (err) {
        if (err && err.message === "sin_api") mensajeSinServidor(msgNueva);
        else if (msgNueva) msgNueva.textContent = "No pude cargar las unidades.";
      });
  }

  function payloadNuevaReserva() {
    return {
      unidad_id: nrUnidad.value,
      check_in: nrCheckin.value,
      check_out: nrCheckout.value,
      huesped_nombre: document.getElementById("nr-nombre").value.trim(),
      huesped_telefono: document.getElementById("nr-telefono").value.trim() || null,
      personas: Number(document.getElementById("nr-personas").value) || 2,
      origen: document.getElementById("nr-origen").value,
      notas_internas: document.getElementById("nr-notas").value.trim() || null,
      promo: "auto",
    };
  }

  var btnNrCotizar = document.getElementById("btn-nr-cotizar");
  if (btnNrCotizar) {
    btnNrCotizar.addEventListener("click", function () {
      if (!apiBase()) {
        mensajeSinServidor(msgNueva);
        return;
      }
      var p = payloadNuevaReserva();
      if (!p.unidad_id || !p.check_in || !p.check_out) {
        if (msgNueva) msgNueva.textContent = "Completá unidad y fechas.";
        return;
      }
      if (msgNueva) msgNueva.textContent = "Cotizando…";
      apiFetch("/api/cotizar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(p),
      })
        .then(function (j) {
          var cot = j.cotizacion || {};
          var disp = j.disponible ? "Hay lugar" : "Sin lugar (solape)";
          if (nrCotizacion) {
            nrCotizacion.hidden = false;
            nrCotizacion.textContent =
              disp +
              " · " +
              (cot.noches || "?") +
              " noche(s) · total " +
              fmtMoney(cot.total, "ARS");
          }
          if (msgNueva) msgNueva.textContent = "";
        })
        .catch(function (err) {
          var t = "No pude cotizar.";
          if (err && err.body && err.body.detail) t = String(err.body.detail);
          if (msgNueva) msgNueva.textContent = t;
        });
    });
  }

  if (nrForm) {
    nrForm.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (!apiBase()) {
        mensajeSinServidor(msgNueva);
        return;
      }
      var btn = document.getElementById("btn-nr-guardar");
      if (btn) {
        btn.disabled = true;
        btn.textContent = "Guardando…";
      }
      if (msgNueva) msgNueva.textContent = "";

      apiFetch("/api/reservas/operacion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payloadNuevaReserva()),
      })
        .then(function (j) {
          nrForm.hidden = true;
          if (nrExito) nrExito.hidden = false;
          var codigoEl = document.getElementById("nr-codigo");
          var resumenEl = document.getElementById("nr-resumen");
          var msgEl = document.getElementById("nr-mensaje-huesped");
          if (codigoEl) codigoEl.textContent = j.codigo_reserva || codigoReserva(j.id);
          if (resumenEl) {
            resumenEl.textContent =
              (j.huesped_nombre || "") +
              " · " +
              fmtFechaISO(j.check_in) +
              " → " +
              fmtFechaISO(j.check_out) +
              " · " +
              fmtMoney(j.precio_total, j.moneda);
          }
          if (msgEl) msgEl.value = j.mensaje_huesped || "";
          var wa = document.getElementById("btn-nr-whatsapp");
          if (wa) {
            var tel = document.getElementById("nr-telefono").value.replace(/\D/g, "");
            var text = encodeURIComponent(j.mensaje_huesped || "");
            wa.href = tel
              ? "https://wa.me/" + tel + "?text=" + text
              : "https://wa.me/5493541571190?text=" + text;
          }
        })
        .catch(function (err) {
          var t = "No se pudo guardar la reserva.";
          if (err && err.body && err.body.detail) t = String(err.body.detail);
          if (msgNueva) msgNueva.textContent = t;
        })
        .finally(function () {
          if (btn) {
            btn.disabled = false;
            btn.textContent = "Confirmar reserva";
          }
        });
    });
  }

  var btnNrCopiar = document.getElementById("btn-nr-copiar-msg");
  if (btnNrCopiar) {
    btnNrCopiar.addEventListener("click", function () {
      var msgEl = document.getElementById("nr-mensaje-huesped");
      if (!msgEl) return;
      navigator.clipboard.writeText(msgEl.value).then(
        function () {
          btnNrCopiar.textContent = "¡Copiado!";
          window.setTimeout(function () {
            btnNrCopiar.textContent = "Copiar mensaje";
          }, 1600);
        },
        function () {
          msgEl.select();
        }
      );
    });
  }

  var btnNrOtra = document.getElementById("btn-nr-otra");
  if (btnNrOtra) {
    btnNrOtra.addEventListener("click", function () {
      if (nrForm) nrForm.reset();
      initNuevaReserva();
    });
  }

  var listaIcal = document.getElementById("lista-ical");

  window.copiadoHint = "";

  function cargarEnlacesIcal() {
    if (!listaIcal) return;
    listaIcal.innerHTML = "<p class=\"cotiza-muted\">Cargando unidades…</p>";

    apiFetch("/api/unidades?solo_alquilables=true")
      .then(function (json) {
        listaIcal.innerHTML = "";

        var base = apiBase() || window.location.origin;
        var items = json.unidades || [];

        items.forEach(function (unidad) {
          var relUrl = "/api/unidades/" + encodeURIComponent(unidad.id) + "/ical";
          var full = base + relUrl;

          var card = document.createElement("article");
          card.className = "ical-card";

          var h = document.createElement("strong");
          h.textContent = unidad.nombre;
          card.appendChild(h);

          var p = document.createElement("p");
          p.className = "ical-muted";
          p.style.fontSize = "0.82rem";
          p.style.margin = "0";
          p.style.color = "var(--muted)";
          p.textContent =
            "Copiá el enlace y pegalo donde Airbnb u otro sistema te deje importar un calendario (ocupación).";
          card.appendChild(p);

          var code = document.createElement("div");
          code.className = "ical-url";
          code.textContent = full;

          card.appendChild(code);

          var row = document.createElement("div");
          row.className = "btn-row";

          var btn = document.createElement("button");
          btn.type = "button";
          btn.className = "btn btn-primary";
          btn.textContent = "Copiar enlace";
          btn.addEventListener("click", function () {
            navigator.clipboard.writeText(full).then(
              function () {
                btn.textContent = "¡Copiado!";
                window.setTimeout(function () {
                  btn.textContent = "Copiar enlace";
                }, 1800);
              },
              function () {
                window.prompt("Copiá este enlace:", full);
              }
            );
          });

          row.appendChild(btn);
          card.appendChild(row);
          listaIcal.appendChild(card);
        });

        if (items.length === 0) {
          listaIcal.textContent =
            "No aparecen unidades alquilables. Revisá configuración desde el equipo técnico.";
        }
      })
      .catch(function () {
        listaIcal.textContent = "No se pudieron obtener las unidades.";
      });
  }

  (function cargarAma() {
    var fase = document.getElementById("ama-fase");
    var det = document.getElementById("ama-detalle");
    if (!fase || !det) return;
    apiFetch("/api/ama/estado")
      .then(function (j) {
        fase.textContent = j.fase || "—";
        det.textContent = j.mensaje || "";
      })
      .catch(function () {
        fase.textContent = "no disponible";
        det.textContent = "No se pudo leer el estado. ¿Está encendido el programa?";
      });
  })();

  function cargarAlertas() {
    var box = document.getElementById("panel-alertas");
    if (!box || !apiBase()) return;
    apiFetch("/api/canales/alertas?solo_no_leidas=true&limite=5")
      .then(function (j) {
        var items = j.alertas || [];
        if (!items.length) {
          box.hidden = true;
          box.innerHTML = "";
          return;
        }
        box.hidden = false;
        box.innerHTML =
          "<strong>Alertas</strong><ul>" +
          items
            .map(function (a) {
              return (
                "<li><span class=\"panel-alerta-tipo\">" +
                (a.titulo || "Aviso") +
                "</span> " +
                (a.mensaje || "").replace(/\n/g, " · ") +
                "</li>"
              );
            })
            .join("") +
          "</ul><button type=\"button\" class=\"btn btn-outline btn-sm\" id=\"btn-alertas-leidas\">Marcar leídas</button>";
        var btn = document.getElementById("btn-alertas-leidas");
        if (btn) {
          btn.addEventListener("click", function () {
            apiFetch("/api/canales/alertas/leer", { method: "POST" }).then(function () {
              cargarAlertas();
            });
          });
        }
      })
      .catch(function () {
        box.hidden = true;
      });
  }

  cargarSiteConfig().then(function () {
    cargarAlertas();
    if (window.location.hash === "#/calendario") {
      showPane("calendario");
      cargarCalendario();
    }
    if (window.location.hash === "#/tarifas") {
      showPane("tarifas");
      cargarTarifasCalendario();
    }
    if (window.location.hash === "#/nueva-reserva") {
      showPane("nueva-reserva");
      initNuevaReserva();
    }
  });

  window.TerraPanel = { showPane: showPane, syncBooking: sincronizarBooking };
})();
