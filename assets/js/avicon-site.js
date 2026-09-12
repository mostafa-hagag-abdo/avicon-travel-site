/* Avicon Travel - the header behaviours the site uses, ported from the old
   theme script (assets/themes/gofly-main/assets/js/custom.js), which also
   pulled in ~20 slider/map/calendar libraries no page needs. */
(function ($) {
  "use strict";
  if (!$) return; // every page loads jQuery before this file; bail out rather than throw if one doesn't

  // mobile menu
  $(".sidebar-button").on("click", function () {
    $(this).toggleClass("active");
    $(".main-menu").toggleClass("show-menu");
  });
  $(".menu-close-btn").on("click", function () {
    $(".main-menu").removeClass("show-menu");
  });

  // sub-menus on mobile
  $(".dropdown-icon").on("click", function () {
    $(this).toggleClass("active").next("ul, .mega-menu").slideToggle();
    $(this).parent().siblings().children("ul, .mega-menu").slideUp();
    $(this).parent().siblings().children(".active").removeClass("active");
  });

  // header search box
  $(".search-btn").on("click", function (e) {
    $(this).parent().find(".search-input").toggleClass("active");
    e.stopPropagation();
  });
  $(document).on("click", function (e) {
    if (!$(e.target).closest(".search-btn, .search-input").length) {
      $(".search-input").removeClass("active");
    }
  });
  $(".search-close").on("click", function () {
    $(".search-input").removeClass("active");
  });

  // sticky header + back-to-top ring
  var header = document.querySelector("header.header-area");
  var wrap = document.querySelector(".progress-wrap");
  var path = wrap && wrap.querySelector(".progress-circle path");
  var length = path ? path.getTotalLength() : 0;
  if (path) {
    path.style.strokeDasharray = length + " " + length;
    path.style.strokeDashoffset = length;
    path.getBoundingClientRect();
    path.style.transition = "stroke-dashoffset 10ms linear";
  }
  function onScroll() {
    var y = window.scrollY;
    if (header) header.classList.toggle("sticky", y > 0);
    if (wrap) {
      wrap.classList.toggle("active-progress", y > 50);
      var height = document.documentElement.scrollHeight - window.innerHeight;
      if (path && height > 0) path.style.strokeDashoffset = length - (y * length) / height;
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  if (wrap) {
    wrap.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
})(window.jQuery);
