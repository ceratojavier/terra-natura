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
        cargarEstadoGmailBooking();
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
      if (target === "recaudacion") {
        initRecaudacion();
      }
    });
  });

  function abrirDesdeHash() {
    var h = window.location.hash;
    if (h === "#/reservas") {
      showPane("reservas");
      cargarReservas();
    }
    if (h === "#/nueva-reserva") {
      showPane("nueva-reserva");
      initNuevaReserva();
    }
    if (h === "#/calendario") {
      showPane("calendario");
      cargarCalendario();
      cargarEstadoGmailBooking();
    }
    if (h === "#/tarifas") {
      showPane("tarifas");
      cargarTarifasCalendario();
    }
    if (h === "#/ical") {
      showPane("ical");
      cargarEnlacesIcal();
    }
    if (h === "#/recaudacion") {
      showPane("recaudacion");
      initRecaudacion();
    }
  }

  window.addEventListener("hashchange", abrirDesdeHash);

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
    cargarEstadoGmailBooking();
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

  function mesRango(ym) {
    var p = (ym || "").split("-");
    var y = Number(p[0] || 0);
    var m = Number(p[1] || 0);
    if (!y || !m) return null;
    var desde = new Date(y, m - 1, 1);
    var hasta = new Date(y, m, 0);
    return { desde: ymdISO(desde), hasta: ymdISO(hasta), ym: y + "-" + String(m).padStart(2, "0") };
  }

  function fmtMesLabel(ym) {
    var r = mesRango(ym);
    if (!r) return ym || "";
    var d = new Date(r.desde + "T12:00:00");
    var s = d.toLocaleDateString("es-AR", { month: "long", year: "numeric" });
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  function shiftMes(ym, delta) {
    var p = (ym || "").split("-");
    var d = new Date(Number(p[0]), Number(p[1] || 1) - 1 + delta, 1);
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0");
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
              nombreLimpio(r) || "—",
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
  var msgGmailBooking = document.getElementById("msg-gmail-booking");
  var calGrid = document.getElementById("calendario-grid");
  var calOcupacionMes = document.getElementById("cal-ocupacion-mes");
  var calMesPrev = document.getElementById("cal-mes-prev");
  var calMesNext = document.getElementById("cal-mes-next");
  var btnVerMesCal = document.getElementById("btn-ver-mes-cal");
  var btnSyncBooking = document.getElementById("btn-sync-booking");
  var btnSyncBookingIcal = document.getElementById("btn-sync-booking-ical");
  var btnRecargarCal = document.getElementById("btn-recargar-cal");
  var msgSyncIcal = document.getElementById("msg-sync-ical");

  function cargarEstadoGmailBooking() {
    if (!msgGmailBooking || !apiBase()) return;
    apiFetch("/api/canales/estado")
      .then(function (j) {
        var g = (j && j.gmail_booking) || {};
        if (g.configurado) {
          var ultimo = g.ultimo_sync || {};
          var extra = "";
          if (ultimo.procesados != null) {
            extra =
              " · última lectura: " +
              (ultimo.procesados || 0) +
              " email(s)";
          }
          msgGmailBooking.className = "cotiza-muted msg-calendario-ok";
          msgGmailBooking.textContent =
            "Gmail conectado (" +
            (g.cuenta || "ceratojavier@gmail.com") +
            "). De cada email de Booking se toma el número de reserva y la fecha " +
            "de entrada. Nombre, teléfono y monto no vienen por email: se cargan " +
            "con el archivo de Booking." +
            extra;
        } else {
          msgGmailBooking.className = "cotiza-muted msg-calendario-err";
          msgGmailBooking.textContent =
            "Gmail todavía no está conectado. Las fechas de Booking sí se sincronizan; para nombre, teléfono y monto hace falta autorizar el correo una sola vez.";
        }
      })
      .catch(function () {
        msgGmailBooking.className = "cotiza-muted";
        msgGmailBooking.textContent = "";
      });
  }

  if (calOcupacionMes && !calOcupacionMes.value) {
    calOcupacionMes.value = new Date().toISOString().slice(0, 7);
  }
  if (calOcupacionMes) {
    calOcupacionMes.addEventListener("change", function () {
      cargarCalendario();
    });
    calOcupacionMes.addEventListener("input", function () {
      cargarCalendario();
    });
  }
  if (btnVerMesCal) {
    btnVerMesCal.addEventListener("click", function () {
      cargarCalendario();
    });
  }
  if (calMesPrev) {
    calMesPrev.addEventListener("click", function () {
      if (!calOcupacionMes) return;
      calOcupacionMes.value = shiftMes(calOcupacionMes.value, -1);
      cargarCalendario();
    });
  }
  if (calMesNext) {
    calMesNext.addEventListener("click", function () {
      if (!calOcupacionMes) return;
      calOcupacionMes.value = shiftMes(calOcupacionMes.value, 1);
      cargarCalendario();
    });
  }

  function sincronizarBooking(btn, msgEl) {
    if (!apiBase()) {
      mensajeSinServidor(msgEl || msgCal);
      return;
    }
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Sincronizando…";
    }
    var targetMsg = msgEl || msgCal;
    if (targetMsg) {
      targetMsg.className = "cotiza-muted";
      targetMsg.textContent = "Leyendo fechas de Booking y datos de Gmail…";
    }

    apiFetch("/api/canales/sync-ical", { method: "POST" })
      .then(function (j) {
        var c = 0;
        var a = 0;
        var o = 0;
        var cancel = 0;
        var errs = [];
        (j.detalle || []).forEach(function (d) {
          c += d.creadas || 0;
          a += d.actualizadas || 0;
          o += d.omitidas || 0;
          cancel += d.canceladas || 0;
          (d.errores || []).forEach(function (e) {
            errs.push(e);
          });
        });
        var txt =
          (j.mensaje ? j.mensaje + " — " : "Booking sincronizado. ") +
          "Nuevas: " +
          (j.nuevas_total != null ? j.nuevas_total : c) +
          " · Actualizadas: " +
          a +
          " · Ya estaban: " +
          o +
          " · Liberadas: " +
          cancel;
        if (errs.length) txt += " · Avisos: " + errs.slice(0, 2).join("; ");
        if ((j.nuevas_total || c) > 0) {
          txt += " — Revisá alertas arriba.";
        }
        if (j.gmail) {
          if (j.gmail.error) {
            txt += " · Gmail no respondió: " + j.gmail.error;
          } else if (j.gmail.configurado) {
            txt +=
              " · Emails de Booking leídos: " +
              (j.gmail.encontrados || 0) +
              " · Estadías identificadas por número: " +
              (j.gmail.procesados || 0);
            if (j.gmail.total_pendientes) {
              txt +=
                " · Sin nombre ni monto: " +
                j.gmail.total_pendientes +
                " (Booking no los manda por email; cargá el archivo de Booking acá abajo)";
            }
            if ((j.gmail.errores || []).length) {
              txt += " · Emails con aviso: " + j.gmail.errores.length;
            }
          } else {
            txt += " · Falta conectar Gmail para traer nombre, teléfono y monto.";
          }
        }
        if (targetMsg) {
          targetMsg.className = "cotiza-muted msg-calendario-ok";
          targetMsg.textContent = txt;
        }
        if (msgCal && msgCal !== targetMsg) {
          msgCal.className = "cotiza-muted msg-calendario-ok";
          msgCal.textContent = txt;
        }
        cargarCalendario();
        cargarEstadoGmailBooking();
        if (tb) cargarReservas();
        cargarAlertas();
      })
      .catch(function (err) {
        var t = "Error al sincronizar Booking. Probá de nuevo.";
        if (err && err.message === "sin_api") mensajeSinServidor(targetMsg || msgCal);
        else if (targetMsg || msgCal) {
          (targetMsg || msgCal).className = "cotiza-muted msg-calendario-err";
          (targetMsg || msgCal).textContent = t;
        }
      })
      .finally(function () {
        if (btn) {
          btn.disabled = false;
          btn.textContent =
            btn.id === "btn-sync-booking"
              ? "Sincronizar Booking (fechas + datos)"
              : "Sincronizar Booking ahora";
        }
      });
  }

  var inputArchivoBooking = document.getElementById("archivo-booking");
  var btnImportarBooking = document.getElementById("btn-importar-booking");
  var msgImportarBooking = document.getElementById("msg-importar-booking");

  function importarArchivoBooking() {
    if (!msgImportarBooking) return;
    var archivo =
      inputArchivoBooking && inputArchivoBooking.files
        ? inputArchivoBooking.files[0]
        : null;
    if (!archivo) {
      msgImportarBooking.className = "cotiza-muted msg-calendario-err";
      msgImportarBooking.textContent = "Elegí primero el archivo que bajaste de Booking.";
      return;
    }
    if (!apiBase()) {
      mensajeSinServidor(msgImportarBooking);
      return;
    }
    var datos = new FormData();
    datos.append("archivo", archivo);
    btnImportarBooking.disabled = true;
    btnImportarBooking.textContent = "Cargando…";
    msgImportarBooking.className = "cotiza-muted";
    msgImportarBooking.textContent = "Leyendo el archivo y buscando cada reserva…";

    apiFetch("/api/canales/importar-reservas-booking", {
      method: "POST",
      body: datos,
    })
      .then(function (j) {
        var txt =
          (j.mensaje || "Listo.") +
          " Nuevas: " +
          (j.creadas || 0) +
          " · Actualizadas (sin duplicar): " +
          (j.reutilizadas || 0) +
          " · Sin cabaña: " +
          (j.total_sin_encontrar || 0) +
          ".";
        if ((j.avisos || []).length) {
          txt += " Avisos: " + j.avisos.slice(0, 2).join(" · ");
        }
        msgImportarBooking.className = "cotiza-muted msg-calendario-ok";
        msgImportarBooking.textContent = txt;
        cargarCalendario();
        if (tb) cargarReservas();
      })
      .catch(function (err) {
        msgImportarBooking.className = "cotiza-muted msg-calendario-err";
        if (err && err.message === "sin_api") {
          mensajeSinServidor(msgImportarBooking);
        } else {
          msgImportarBooking.textContent =
            (err && err.body && err.body.detail) ||
            "No pude leer el archivo. Bajalo de nuevo desde Booking sin abrirlo.";
        }
      })
      .finally(function () {
        btnImportarBooking.disabled = false;
        btnImportarBooking.textContent = "Cargar archivo XLS";
      });
  }

  if (btnImportarBooking) {
    btnImportarBooking.addEventListener("click", importarArchivoBooking);
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
    btnRecargarCal.addEventListener("click", function () {
      cargarCalendario();
    });
  }

  var calReservasBox = document.getElementById("calendario-reservas");
  var calDetalleBox = document.getElementById("calendario-detalle");
  var calUnidades = [];

  function nombreUnidad(id, units) {
    var lista = units || calUnidades;
    for (var i = 0; i < lista.length; i++) {
      if (lista[i].id === id) return lista[i].nombre;
    }
    return id;
  }

  function fmtMoney(n) {
    if (n == null || n === "" || isNaN(Number(n))) return "—";
    return "$" + Math.round(Number(n)).toLocaleString("es-AR");
  }

  function fmtFechaAr(iso) {
    var p = String(iso || "").slice(0, 10).split("-");
    return p.length === 3 ? p[2] + "/" + p[1] + "/" + p[0] : String(iso || "—");
  }

  function noches(r) {
    var a = new Date(String(r.check_in).slice(0, 10) + "T12:00:00");
    var b = new Date(String(r.check_out).slice(0, 10) + "T12:00:00");
    var n = Math.round((b - a) / 86400000);
    return n > 0 ? n : 1;
  }

  function nombreLimpio(r) {
    var n = (r.huesped_nombre || "").trim();
    if (!n || /closed|not available|^reserva booking$|^import /i.test(n)) return "";
    return n;
  }

  function esPasada(r) {
    return String(r.check_out).slice(0, 10) <= new Date().toISOString().slice(0, 10);
  }

  function estadoReserva(r) {
    if (r.estado === "cancelada" || r.estado === "no_show") return "cancelada";
    if (esPasada(r)) return "pasada";
    return "activa";
  }

  function etiquetaEstado(r) {
    var e = estadoReserva(r);
    if (e === "cancelada") return { clase: "cal-badge-cancelada", texto: "Cancelada" };
    if (e === "pasada") return { clase: "cal-badge-pasada", texto: "Ya pasó" };
    return { clase: "cal-badge-activa", texto: "Por venir" };
  }

  function etiquetaCortaReserva(r) {
    var n = nombreLimpio(r) || "Booking";
    var corto = n.split(/\s+/).slice(0, 2).join(" ");
    if (r.precio_total > 0) return corto + " · " + fmtMoney(r.precio_total);
    if (r.precio_usd > 0) return corto + " · U$S " + Number(r.precio_usd);
    return corto;
  }

  function cerrarDetalle() {
    if (!calDetalleBox) return;
    calDetalleBox.hidden = true;
    calDetalleBox.innerHTML = "";
    var activas = calGrid ? calGrid.querySelectorAll(".cal-activa") : [];
    for (var i = 0; i < activas.length; i++) {
      activas[i].classList.remove("cal-activa");
    }
  }

  function formularioReserva(r) {
    var form = document.createElement("div");
    form.className = "cal-reserva-form";
    form.innerHTML =
      "<label>Nombre del cliente<input data-f=\"nombre\" type=\"text\" value=\"" +
      nombreLimpio(r).replace(/"/g, "&quot;") +
      "\" placeholder=\"Como figura en Booking\"></label>" +
      "<label>Teléfono<input data-f=\"tel\" type=\"tel\" value=\"" +
      (r.huesped_telefono || "") +
      "\" placeholder=\"Ej. 351...\"></label>" +
      "<label>Monto USD<input data-f=\"usd\" type=\"number\" min=\"0\" step=\"0.01\" value=\"" +
      (r.precio_usd || "") +
      "\" placeholder=\"Total estadía en USD\"></label>" +
      "<label>Día que reservó<input data-f=\"fecha\" type=\"date\" value=\"" +
      (r.fecha_reserva_ota || "") +
      "\"></label>" +
      "<button type=\"button\" class=\"btn btn-primary\" data-save>Guardar + pasar a pesos</button>";
    var btn = form.querySelector("[data-save]");
    btn.addEventListener("click", function () {
      var payload = {
        huesped_nombre: form.querySelector('[data-f="nombre"]').value.trim() || null,
        huesped_telefono: form.querySelector('[data-f="tel"]').value.trim() || null,
        precio_usd: form.querySelector('[data-f="usd"]').value
          ? Number(form.querySelector('[data-f="usd"]').value)
          : null,
        fecha_reserva_ota: form.querySelector('[data-f="fecha"]').value || null,
      };
      btn.disabled = true;
      btn.textContent = "Guardando…";
      apiFetch("/api/reservas/" + encodeURIComponent(r.id) + "/enriquecer-booking", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
        .then(function () {
          if (msgCal) {
            msgCal.className = "cotiza-muted msg-calendario-ok";
            msgCal.textContent = "Datos del huésped guardados. Monto pasado a pesos.";
          }
          cargarCalendario(r.id);
        })
        .catch(function () {
          if (msgCal) {
            msgCal.className = "cotiza-muted msg-calendario-err";
            msgCal.textContent = "No pude guardar. Revisá el monto en dólares y la fecha.";
          }
        })
        .finally(function () {
          btn.disabled = false;
          btn.textContent = "Guardar + pasar a pesos";
        });
    });
    return form;
  }

  function mostrarDetalle(r, opciones) {
    if (!calDetalleBox) return;
    var opts = opciones || {};
    calDetalleBox.innerHTML = "";
    calDetalleBox.hidden = false;

    var cerrar = document.createElement("button");
    cerrar.type = "button";
    cerrar.className = "cal-detalle-cerrar";
    cerrar.setAttribute("aria-label", "Cerrar detalle");
    cerrar.innerHTML = "&times;";
    cerrar.addEventListener("click", cerrarDetalle);
    calDetalleBox.appendChild(cerrar);

    var badge = etiquetaEstado(r);
    var h = document.createElement("h3");
    h.innerHTML =
      nombreUnidad(r.unidad_id) +
      " — " +
      (nombreLimpio(r) || "sin nombre cargado") +
      " <span class=\"cal-badge " +
      badge.clase +
      "\">" +
      badge.texto +
      "</span>";
    calDetalleBox.appendChild(h);

    var dl = document.createElement("dl");
    function fila(k, v) {
      var dt = document.createElement("dt");
      dt.textContent = k;
      var dd = document.createElement("dd");
      dd.textContent = v;
      dl.appendChild(dt);
      dl.appendChild(dd);
    }
    fila("Entrada", fmtFechaAr(r.check_in));
    fila("Salida", fmtFechaAr(r.check_out));
    fila("Noches", String(noches(r)));
    fila("Viene de", r.origen === "booking" ? "Booking" : r.origen || "reserva directa");
    fila("Personas", String(r.personas || 2));
    fila("Teléfono", r.huesped_telefono || "todavía no cargado");
    fila(
      "Monto",
      r.precio_total > 0
        ? fmtMoney(r.precio_total) + " en pesos"
        : r.precio_usd > 0
          ? "U$S " + r.precio_usd + " — falta pasarlo a pesos"
          : "todavía no cargado"
    );
    if (r.precio_usd > 0) fila("En dólares", "U$S " + Number(r.precio_usd).toLocaleString("es-AR"));
    if (r.comision_usd != null && r.comision_usd !== "") {
      fila(
        "Comisión Booking",
        "U$S " +
          Number(r.comision_usd).toLocaleString("es-AR") +
          (r.comision_ars
            ? " · " + fmtMoney(r.comision_ars) + " en pesos"
            : "")
      );
    }
    if (r.cotizacion_usd_ars) {
      var dtCot = document.createElement("dt");
      dtCot.textContent = "Dólar Bloomberg";
      var ddCot = document.createElement("dd");
      var txtCot =
        Number(r.cotizacion_usd_ars).toLocaleString("es-AR") +
        (r.cotizacion_fecha ? " del " + fmtFechaAr(r.cotizacion_fecha) : "");
      ddCot.appendChild(document.createTextNode(txtCot + " "));
      var linkBb = document.createElement("a");
      linkBb.href =
        r.cotizacion_url ||
        "https://www.bloomberg.com/quote/USDARS:CUR";
      linkBb.target = "_blank";
      linkBb.rel = "noopener";
      linkBb.textContent = "Ver cotización de ese día";
      ddCot.appendChild(linkBb);
      dl.appendChild(dtCot);
      dl.appendChild(ddCot);
    } else if (r.precio_usd > 0) {
      var dtPend = document.createElement("dt");
      dtPend.textContent = "Dólar Bloomberg";
      var ddPend = document.createElement("dd");
      ddPend.appendChild(document.createTextNode("Pendiente · "));
      var linkPend = document.createElement("a");
      linkPend.href =
        r.cotizacion_url ||
        "https://www.bloomberg.com/quote/USDARS:CUR";
      linkPend.target = "_blank";
      linkPend.rel = "noopener";
      linkPend.textContent = "Abrir Bloomberg";
      ddPend.appendChild(linkPend);
      dl.appendChild(dtPend);
      dl.appendChild(ddPend);
    }
    if (r.fecha_reserva_ota) fila("Reservó el", fmtFechaAr(r.fecha_reserva_ota));
    if (r.booking_reservation_id) {
      fila("Nº de reserva Booking", r.booking_reservation_id);
    }
    if (r.booking_email_recibido_en) {
      fila("Email recibido", fmtFechaAr(r.booking_email_recibido_en));
    }
    if (r.codigo_reserva) fila("Referencia", r.codigo_reserva);
    calDetalleBox.appendChild(dl);

    calDetalleBox.appendChild(formularioReserva(r));

    if (opts.scroll !== false) {
      calDetalleBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }

  function renderReservasMes(reservas, units) {
    if (!calReservasBox) return;
    calReservasBox.innerHTML = "";
    var lista = (reservas || []).slice().sort(function (a, b) {
      return String(a.check_in).localeCompare(String(b.check_in));
    });
    if (!lista.length) {
      calReservasBox.innerHTML =
        "<p class=\"cotiza-muted\">Este mes no tuvo reservas. Si Booking tiene algo nuevo, tocá <strong>Sincronizar Booking</strong>.</p>";
      return;
    }
    var title = document.createElement("h3");
    title.style.margin = "0 0 0.35rem";
    title.style.fontSize = "1.05rem";
    title.textContent = "Estadías de este mes (" + lista.length + ") — tocá una para ver el detalle";
    calReservasBox.appendChild(title);

    lista.forEach(function (r) {
      var card = document.createElement("article");
      card.className = "cal-reserva-card";
      card.tabIndex = 0;
      card.style.cursor = "pointer";

      var badge = etiquetaEstado(r);
      var h = document.createElement("h3");
      h.innerHTML =
        nombreUnidad(r.unidad_id, units) +
        " · " +
        (r.origen === "booking" ? "Booking" : r.origen || "reserva") +
        " <span class=\"cal-badge " +
        badge.clase +
        "\">" +
        badge.texto +
        "</span>";
      card.appendChild(h);

      var meta = document.createElement("p");
      meta.className = "cal-reserva-meta";
      var monto =
        r.precio_total > 0
          ? fmtMoney(r.precio_total)
          : r.precio_usd > 0
            ? "U$S " + r.precio_usd
            : "monto pendiente";
      meta.innerHTML =
        "<strong>" +
        fmtFechaAr(r.check_in) +
        " → " +
        fmtFechaAr(r.check_out) +
        "</strong> · " +
        noches(r) +
        " noche(s)<br>" +
        (nombreLimpio(r) || "sin nombre") +
        " · " +
        (r.huesped_telefono || "sin teléfono") +
        "<br>" +
        monto;
      card.appendChild(meta);

      function abrir() {
        mostrarDetalle(r);
      }
      card.addEventListener("click", abrir);
      card.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          abrir();
        }
      });
      calReservasBox.appendChild(card);
    });
  }

  function cargarCalendario(abrirReservaId) {
    if (!calGrid || !msgCal) return;
    calGrid.innerHTML = "";
    if (calReservasBox) calReservasBox.innerHTML = "";
    if (!abrirReservaId) cerrarDetalle();
    msgCal.className = "cotiza-muted";
    msgCal.textContent = "Cargando calendario…";

    if (!apiBase()) {
      mensajeSinServidor(msgCal);
      return;
    }

    var ym = calOcupacionMes && calOcupacionMes.value;
    if (!ym) {
      ym = new Date().toISOString().slice(0, 7);
      if (calOcupacionMes) calOcupacionMes.value = ym;
    }
    var rango = mesRango(ym);
    if (!rango) {
      msgCal.textContent = "Elegí un mes válido.";
      return;
    }
    var desde = rango.desde;
    var hasta = rango.hasta;

    apiFetch("/api/unidades?solo_alquilables=true")
      .then(function (json) {
        var units = json.unidades || [];
        if (!units.length) {
          msgCal.textContent = "No hay unidades configuradas.";
          return;
        }
        calUnidades = units;

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

        var pReservas = apiFetch(
          "/api/reservas?desde=" +
            encodeURIComponent(desde) +
            "&hasta=" +
            encodeURIComponent(hasta)
        ).catch(function () {
          return [];
        });

        return Promise.all([Promise.all(promises), pReservas]).then(function (pair) {
          return { rows: pair[0], reservas: pair[1] || [], units: units };
        });
      })
      .then(function (pack) {
        if (!pack || !pack.rows) return;
        var rows = pack.rows;
        var reservas = pack.reservas || [];
        var units = pack.units || [];
        var vivas = reservas.filter(function (r) {
          return r.estado !== "cancelada" && r.estado !== "no_show";
        });
        var canceladas = reservas.length - vivas.length;
        msgCal.textContent =
          fmtMesLabel(ym) +
          " · " +
          rows[0].dias.length +
          " noches · " +
          vivas.length +
          " estadía(s)" +
          (canceladas ? " + " + canceladas + " cancelada(s)" : "") +
          " · tocá una noche en rojo para el detalle";

        var fechas = rows[0].dias.map(function (d) {
          return d.fecha;
        });

        function claveDia(unidadId, d) {
          return (
            unidadId +
            "|" +
            d.getFullYear() +
            "-" +
            String(d.getMonth() + 1).padStart(2, "0") +
            "-" +
            String(d.getDate()).padStart(2, "0")
          );
        }

        var porUnidadFecha = {};
        var canceladasPorFecha = {};
        reservas.forEach(function (r) {
          var destino = estadoReserva(r) === "cancelada" ? canceladasPorFecha : porUnidadFecha;
          var cur = new Date(String(r.check_in).slice(0, 10) + "T12:00:00");
          var end = new Date(String(r.check_out).slice(0, 10) + "T12:00:00");
          while (cur < end) {
            destino[claveDia(r.unidad_id, cur)] = r;
            cur.setDate(cur.getDate() + 1);
          }
        });

        var table = document.createElement("table");
        table.className = "calendario-table";

        var thead = document.createElement("thead");
        var hr = document.createElement("tr");
        var th0 = document.createElement("th");
        th0.textContent = "Unidad";
        th0.className = "cal-sticky-unidad";
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
          tdName.className = "cal-sticky-unidad";
          tdName.textContent = row.unidad.nombre;
          tr.appendChild(tdName);

          var mapa = {};
          row.dias.forEach(function (d) {
            mapa[d.fecha] = d.disponible;
          });

          fechas.forEach(function (f) {
            var td = document.createElement("td");
            var libre = mapa[f] === true;
            var clave = row.unidad.id + "|" + f;
            var res = porUnidadFecha[clave] || (libre ? canceladasPorFecha[clave] : null);
            td.className = libre ? "cal-libre" : "cal-ocupado";
            if (res) {
              var est = estadoReserva(res);
              td.className =
                (est === "cancelada"
                  ? "cal-cancelada"
                  : est === "pasada"
                    ? "cal-pasada"
                    : "cal-ocupado") + " has-label cal-clickable";
              td.setAttribute("data-res-id", res.id);
              td.tabIndex = 0;
              var span = document.createElement("span");
              span.className = "cal-cell-label";
              span.textContent = etiquetaCortaReserva(res);
              td.appendChild(span);
              td.title =
                (nombreLimpio(res) || "Sin nombre") +
                " · " +
                fmtFechaAr(res.check_in) +
                " → " +
                fmtFechaAr(res.check_out) +
                (res.huesped_telefono ? " · " + res.huesped_telefono : "") +
                (res.precio_total > 0 ? " · " + fmtMoney(res.precio_total) : "") +
                " — tocá para ver el detalle";
              td.setAttribute("aria-label", td.title);
              (function (reserva, celda) {
                function abrir() {
                  cerrarDetalle();
                  celda.classList.add("cal-activa");
                  mostrarDetalle(reserva);
                }
                celda.addEventListener("click", abrir);
                celda.addEventListener("keydown", function (e) {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    abrir();
                  }
                });
              })(res, td);
            } else {
              td.setAttribute("aria-label", libre ? "Libre" : "Ocupado");
            }
            tr.appendChild(td);
          });
          tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        calGrid.appendChild(table);
        renderReservasMes(reservas, units);

        if (abrirReservaId) {
          for (var i = 0; i < reservas.length; i++) {
            if (reservas[i].id === abrirReservaId) {
              mostrarDetalle(reservas[i], { scroll: false });
              break;
            }
          }
        }
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
        th0.className = "cal-sticky-unidad";
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
          thn.className = "cal-sticky-unidad";
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

  function ultimoDiaMes(ym) {
    var p = (ym || "").split("-");
    if (p.length < 2) return "";
    var y = Number(p[0]);
    var m = Number(p[1]);
    var d = new Date(y, m, 0);
    return (
      y +
      "-" +
      String(m).padStart(2, "0") +
      "-" +
      String(d.getDate()).padStart(2, "0")
    );
  }

  function initRecaudacion() {
    var mes = document.getElementById("rec-mes");
    var desde = document.getElementById("rec-desde");
    var hasta = document.getElementById("rec-hasta");
    if (mes && !mes.value) {
      mes.value = new Date().toISOString().slice(0, 7);
    }
    if (mes && mes.value && desde && hasta && !desde.value) {
      desde.value = mes.value + "-01";
      hasta.value = ultimoDiaMes(mes.value);
    }
    cargarRecaudacion();
  }

  function cargarRecaudacion() {
    var msg = document.getElementById("msg-recaudacion");
    var box = document.getElementById("rec-totales");
    var tb = document.getElementById("tabla-recaudacion-body");
    var desdeEl = document.getElementById("rec-desde");
    var hastaEl = document.getElementById("rec-hasta");
    var origenEl = document.getElementById("rec-origen");
    var mesEl = document.getElementById("rec-mes");
    if (!apiBase()) {
      mensajeSinServidor(msg);
      return;
    }
    if (mesEl && mesEl.value && (!desdeEl.value || !hastaEl.value)) {
      desdeEl.value = mesEl.value + "-01";
      hastaEl.value = ultimoDiaMes(mesEl.value);
    }
    var desde = (desdeEl && desdeEl.value) || "";
    var hasta = (hastaEl && hastaEl.value) || "";
    if (!desde || !hasta) {
      if (msg) {
        msg.textContent = "Elegí un mes o un rango de fechas.";
      }
      return;
    }
    var origen = (origenEl && origenEl.value) || "";
    var q =
      "/api/reservas-resumen?desde=" +
      encodeURIComponent(desde) +
      "&hasta=" +
      encodeURIComponent(hasta);
    if (origen) q += "&origen=" + encodeURIComponent(origen);
    if (msg) {
      msg.className = "cotiza-muted";
      msg.textContent = "Calculando…";
    }
    apiFetch(q)
      .then(function (j) {
        if (msg) {
          msg.className = "cotiza-muted msg-calendario-ok";
          msg.textContent =
            "Período " +
            fmtFechaAr(j.desde) +
            " → " +
            fmtFechaAr(j.hasta) +
            " · " +
            (j.cantidad_activas || 0) +
            " activas · " +
            (j.cantidad_canceladas || 0) +
            " canceladas.";
        }
        if (box) {
          box.hidden = false;
          box.innerHTML =
            "<h3 style=\"margin:0 0 0.5rem;\">Totales</h3>" +
            "<p style=\"margin:0.25rem 0;\"><strong>Recaudado:</strong> " +
            fmtMoney(j.total_recaudado_ars) +
            (j.total_recaudado_usd
              ? " · U$S " + Number(j.total_recaudado_usd).toLocaleString("es-AR")
              : "") +
            "</p>" +
            "<p style=\"margin:0.25rem 0;\"><strong>Comisiones Booking:</strong> " +
            fmtMoney(j.total_comisiones_ars) +
            (j.total_comisiones_usd
              ? " · U$S " + Number(j.total_comisiones_usd).toLocaleString("es-AR")
              : "") +
            "</p>" +
            "<p style=\"margin:0.25rem 0;\"><strong>Neto estimado:</strong> " +
            fmtMoney(j.neto_estimado_ars) +
            "</p>" +
            "<p style=\"margin:0.25rem 0;font-size:0.85rem;opacity:0.85;\">Booking: " +
            (j.cantidad_booking || 0) +
            " · Manuales: " +
            (j.cantidad_manual || 0) +
            "</p>";
        }
        if (tb) {
          tb.innerHTML = "";
          (j.reservas || []).forEach(function (r) {
            var tr = document.createElement("tr");
            [
              fmtFechaAr(r.check_in),
              nombreUnidad(r.unidad_id),
              nombreLimpio(r) || "—",
              r.origen === "booking" ? "Booking" : r.origen || "manual",
              r.precio_usd ? "U$S " + Number(r.precio_usd).toLocaleString("es-AR") : "—",
              r.precio_total > 0 ? fmtMoney(r.precio_total) : "—",
              r.comision_usd != null
                ? "U$S " + Number(r.comision_usd).toLocaleString("es-AR")
                : "—",
              r.comision_ars != null ? fmtMoney(r.comision_ars) : "—",
              r.estado || "—",
            ].forEach(function (txt) {
              var td = document.createElement("td");
              td.textContent = txt;
              tr.appendChild(td);
            });
            tb.appendChild(tr);
          });
        }
      })
      .catch(function (err) {
        if (msg) {
          msg.className = "cotiza-muted msg-calendario-err";
          msg.textContent =
            err && err.message === "sin_api"
              ? "Falta el servidor."
              : "No pude cargar la recaudación.";
        }
      });
  }

  var btnRecFiltrar = document.getElementById("btn-rec-filtrar");
  if (btnRecFiltrar) {
    btnRecFiltrar.addEventListener("click", cargarRecaudacion);
  }
  var recMes = document.getElementById("rec-mes");
  if (recMes) {
    recMes.addEventListener("change", function () {
      var desde = document.getElementById("rec-desde");
      var hasta = document.getElementById("rec-hasta");
      if (recMes.value && desde && hasta) {
        desde.value = recMes.value + "-01";
        hasta.value = ultimoDiaMes(recMes.value);
      }
      cargarRecaudacion();
    });
  }

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
      cargarEstadoGmailBooking();
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
