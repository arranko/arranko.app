/* arranko.app motion: scroll reveals, the kcal counter, macro bars and a gentle parallax.
   Runs only when <head> switched motion on (html.motion). No libraries, no tracking. */
(function () {
  var d = document.documentElement;

  // The light/dark switch in the header: remembers the choice on this device.
  var themeBtn = document.querySelector(".theme");
  if (themeBtn) themeBtn.addEventListener("click", function () {
    var current = d.getAttribute("data-theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    var next = current === "dark" ? "light" : "dark";
    d.setAttribute("data-theme", next);
    try { localStorage.setItem("arranko-theme", next); } catch (e) {}
  });

  // The menu button on narrower screens: opens and closes the menu panel; a tapped link,
  // a tap outside or Escape closes it.
  var top = document.querySelector(".top");
  var menuBtn = document.querySelector(".menu-btn");
  function setMenu(open) {
    if (!top || !menuBtn) return;
    top.classList.toggle("open", open);
    menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
  }
  if (menuBtn) {
    menuBtn.addEventListener("click", function () { setMenu(!top.classList.contains("open")); });
    document.querySelectorAll(".menu a").forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
    document.addEventListener("click", function (e) { if (top.classList.contains("open") && !top.contains(e.target)) setMenu(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
  }

  if (!d.classList.contains("motion")) return;
  d.classList.add("motion-ready");

  // Number children of staggered groups so each arrives a little after the previous one.
  document.querySelectorAll(".stagger").forEach(function (group) {
    Array.prototype.forEach.call(group.children, function (child, i) { child.style.setProperty("--n", i); });
  });

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      // Shown when it comes into view, or straight away if the page was opened or jumped past it.
      if (!entry.isIntersecting && entry.boundingClientRect.top > 0) return;
      entry.target.classList.add("in");
      io.unobserve(entry.target);
    });
  }, { rootMargin: "0px 0px -10% 0px", threshold: 0.12 });
  document.querySelectorAll(".reveal, .stagger").forEach(function (el) { io.observe(el); });

  // The Today screen: once the phone has arrived, count the numbers up from zero (700 ms, like the
  // approved screen), and move the ring and the bars.
  var show = document.querySelector(".showcase.main");
  if (show) {
    var start = (d.classList.contains("splashing") ? 3050 : 150) + 1300;
    var nums = show.querySelectorAll("[data-count]");
    var ring = show.querySelector(".t-ring");
    var bars = show.querySelectorAll(".t-bar");
    var ringTo = ring ? ring.getAttribute("stroke-dashoffset") : null;
    var barTo = Array.prototype.map.call(bars, function (b) { return b.getAttribute("width"); });
    nums.forEach(function (n) { n.textContent = n.getAttribute("data-down") || "0"; });
    if (ring) ring.setAttribute("stroke-dashoffset", "314.16");
    bars.forEach(function (b) { b.setAttribute("width", "0%"); });
    setTimeout(function () {
      if (ring) ring.setAttribute("stroke-dashoffset", ringTo);
      bars.forEach(function (b, i) { b.setAttribute("width", barTo[i]); });
      var t0 = null, dur = 700;
      function step(t) {
        if (t0 === null) t0 = t;
        var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3);
        nums.forEach(function (n) {
          var to = parseInt(n.getAttribute("data-count"), 10), from = parseInt(n.getAttribute("data-down") || "0", 10);
          n.textContent = Math.round(from + (to - from) * e);
        });
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }, start);

    // Parallax on wide screens: the phone drifts up a little as the page scrolls (never out of the block).
    var wide = window.matchMedia("(min-width: 901px)");
    var ticking = false;
    window.addEventListener("scroll", function () {
      if (!wide.matches || ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        show.style.translate = "0 " + (-Math.min(window.scrollY, 700) * 0.06) + "px";
        ticking = false;
      });
    }, { passive: true });
  }
})();
