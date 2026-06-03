(function () {
  function initGalleryCarousel(carousel) {
    if (!carousel || carousel.getAttribute("data-carousel-ready") === "1") return;

    var gallerySlides = carousel.querySelectorAll(".gallery-slide");
    if (!gallerySlides.length) return;

    carousel.setAttribute("data-carousel-ready", "1");
    var prev = carousel.querySelector(".gallery-nav--prev");
    var next = carousel.querySelector(".gallery-nav--next");
    var dotsWrap = carousel.querySelector(".gallery-dots");
    var gidx = 0;
    var timer = null;

    function renderDots() {
      if (!dotsWrap) return;
      dotsWrap.innerHTML = "";
      gallerySlides.forEach(function (_, i) {
        var d = document.createElement("button");
        d.type = "button";
        d.className = "gallery-dot" + (i === gidx ? " is-active" : "");
        d.setAttribute("aria-label", "Foto " + (i + 1));
        d.addEventListener("click", function () {
          go(i);
          play();
        });
        dotsWrap.appendChild(d);
      });
    }

    function go(i) {
      gallerySlides[gidx].classList.remove("is-active");
      gidx = (i + gallerySlides.length) % gallerySlides.length;
      gallerySlides[gidx].classList.add("is-active");
      renderDots();
    }

    function play() {
      if (gallerySlides.length <= 1) return;
      clearInterval(timer);
      timer = setInterval(function () {
        go(gidx + 1);
      }, 4600);
    }

    if (prev) {
      prev.addEventListener("click", function () {
        go(gidx - 1);
        play();
      });
    }
    if (next) {
      next.addEventListener("click", function () {
        go(gidx + 1);
        play();
      });
    }

    renderDots();
    play();
  }

  window.TN_initGalleryCarousel = initGalleryCarousel;

  var items = document.querySelectorAll(".reveal");
  if (items.length && "IntersectionObserver" in window) {
    var obs = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            obs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.14, rootMargin: "0px 0px -6% 0px" }
    );

    items.forEach(function (el) {
      obs.observe(el);
    });
  }

  var slides = document.querySelectorAll(".hero-slide");
  var idx = 0;
  if (slides.length > 1) {
    setInterval(function () {
      slides[idx].classList.remove("is-active");
      idx = (idx + 1) % slides.length;
      slides[idx].classList.add("is-active");
    }, 5200);
  }

  var glow = document.querySelector(".hero-glow");
  if (glow) {
    window.addEventListener("mousemove", function (ev) {
      var x = (ev.clientX / window.innerWidth - 0.5) * 20;
      var y = (ev.clientY / window.innerHeight - 0.5) * 20;
      glow.style.transform = "translate(" + x + "px," + y + "px)";
    });
  }

  document.querySelectorAll("[data-gallery-carousel]").forEach(initGalleryCarousel);
})();
