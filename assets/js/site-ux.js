(function () {
  function initGalleryCarousel(carousel) {
    if (!carousel || carousel.getAttribute("data-carousel-ready") === "1") return;

    if (carousel.getAttribute("data-carousel-ready") === "1") return;
    var gallerySlides = function () { return carousel.querySelectorAll(".gallery-slide"); };
    if (!gallerySlides().length) return;

    carousel.setAttribute("data-carousel-ready", "1");
    var prev = carousel.querySelector(".gallery-nav--prev");
    var next = carousel.querySelector(".gallery-nav--next");
    var dotsWrap = carousel.querySelector(".gallery-dots");
    var gidx = 0;
    var timer = null;

    function renderDots() {
      if (!dotsWrap) return;
      dotsWrap.innerHTML = "";
      gallerySlides().forEach(function (_, i) {
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
      var slidesNow = gallerySlides();
      if (!slidesNow.length) return;
      slidesNow.forEach(function (slide, index) { slide.classList.toggle("is-active", index === (i + slidesNow.length) % slidesNow.length); });
      gidx = (i + slidesNow.length) % slidesNow.length;
      renderDots();
    }

    function play() {
      if (gallerySlides().length <= 1) return;
      clearInterval(timer);
      timer = setInterval(function () {
        go(gidx + 1);
      }, 4600);
    }

    carousel._tnRefreshGallery = function () { gidx = 0; go(0); play(); };

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
  window.TN_refreshGalleryCarousels = function () {
    document.querySelectorAll("[data-gallery-carousel]").forEach(function (carousel) {
      if (carousel.getAttribute("data-carousel-ready") === "1") {
        if (typeof carousel._tnRefreshGallery === "function") carousel._tnRefreshGallery();
      } else {
        initGalleryCarousel(carousel);
      }
    });
  };

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

  var heroIdx = 0;
  var heroTimer = null;
  function refreshHeroSlides() {
    var slides = document.querySelectorAll(".hero-slide");
    heroIdx = 0;
    slides.forEach(function (slide, index) { slide.classList.toggle("is-active", index === 0); });
    clearInterval(heroTimer);
    if (slides.length > 1) {
      heroTimer = setInterval(function () {
        var current = document.querySelectorAll(".hero-slide");
        if (current.length < 2) return;
        current[heroIdx].classList.remove("is-active");
        heroIdx = (heroIdx + 1) % current.length;
        current[heroIdx].classList.add("is-active");
      }, 5200);
    }
  }
  window.TN_refreshHeroSlides = refreshHeroSlides;
  refreshHeroSlides();

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
