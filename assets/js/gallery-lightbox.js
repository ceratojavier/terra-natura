/** Lightbox simple para galerías de cabaña */
(function () {
  function init(root) {
    var imgs = root.querySelectorAll("[data-lightbox]");
    if (!imgs.length) return;

    var overlay = document.createElement("div");
    overlay.className = "lightbox-overlay";
    overlay.hidden = true;
    overlay.innerHTML =
      '<button type="button" class="lightbox-close" aria-label="Cerrar">×</button>' +
      '<button type="button" class="lightbox-prev" aria-label="Anterior">‹</button>' +
      '<img class="lightbox-img" alt="" />' +
      '<button type="button" class="lightbox-next" aria-label="Siguiente">›</button>' +
      '<p class="lightbox-caption"></p>';
    document.body.appendChild(overlay);

    var list = Array.from(imgs).map(function (el) {
      return { src: el.getAttribute("data-lightbox") || el.src, alt: el.alt || "" };
    });
    var idx = 0;
    var imgEl = overlay.querySelector(".lightbox-img");
    var cap = overlay.querySelector(".lightbox-caption");

    function show(i) {
      idx = (i + list.length) % list.length;
      imgEl.src = list[idx].src;
      imgEl.alt = list[idx].alt;
      cap.textContent = list[idx].alt + " · " + (idx + 1) + "/" + list.length;
      overlay.hidden = false;
      document.body.style.overflow = "hidden";
    }

    function hide() {
      overlay.hidden = true;
      document.body.style.overflow = "";
    }

    imgs.forEach(function (el, i) {
      el.style.cursor = "zoom-in";
      el.addEventListener("click", function (e) {
        e.preventDefault();
        show(i);
      });
    });

    overlay.querySelector(".lightbox-close").addEventListener("click", hide);
    overlay.querySelector(".lightbox-prev").addEventListener("click", function () {
      show(idx - 1);
    });
    overlay.querySelector(".lightbox-next").addEventListener("click", function () {
      show(idx + 1);
    });
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) hide();
    });
    document.addEventListener("keydown", function (e) {
      if (overlay.hidden) return;
      if (e.key === "Escape") hide();
      if (e.key === "ArrowLeft") show(idx - 1);
      if (e.key === "ArrowRight") show(idx + 1);
    });
  }

  document.querySelectorAll("[data-gallery]").forEach(init);
})();
