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
      if (target === "reservas") {
        cargarReservas();
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
  });

  if (window.location.hash === "#/reservas") {
    showPane("reservas");
    cargarReservas();
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
          "Creadas: " +
          c +
          " · Actualizadas: " +
          a +
          " · Omitidas: " +
          o;
        if (msgEl) msgEl.textContent = txt;
        if (msgCal) msgCal.textContent = txt;
        cargarCalendario();
        if (tb) cargarReservas();
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

  cargarSiteConfig().then(function () {
    if (window.location.hash === "#/calendario") {
      showPane("calendario");
      cargarCalendario();
    }
  });

  window.TerraPanel = { showPane: showPane, syncBooking: sincronizarBooking };
})();
