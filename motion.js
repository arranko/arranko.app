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

  // Phones in the hero: a tap, click, Enter or Space opens the phone big in the middle of the
  // screen (upright, as large as fits); ✕, a tap outside it or Escape closes it.
  var fans = document.querySelectorAll(".fan");
  var closeLabel = d.lang === "es" ? "Cerrar" : "Close";
  var openLabel = d.lang === "es" ? "Ver esta pantalla en grande" : "See this screen big";
  function openViewer(fan) {
    var fig = fan.querySelector(".showcase");
    if (!fig) return;
    var clone = fig.cloneNode(true);
    clone.querySelectorAll("[data-count]").forEach(function (n) { n.textContent = n.getAttribute("data-count"); });
    var ring = clone.querySelector(".t-ring"); if (ring) ring.setAttribute("stroke-dashoffset", "194.03");
    var bars = clone.querySelectorAll(".t-bar"), widths = ["75%", "35%", "15.9%"];
    bars.forEach(function (b, i) { b.setAttribute("width", widths[i] || b.getAttribute("width")); });
    var s = Math.min(1, (window.innerHeight - 48) / 864, (window.innerWidth - 32) / 410);
    clone.style.setProperty("--s", s.toFixed(3));
    clone.removeAttribute("aria-hidden");
    var v = document.createElement("div");
    v.className = "viewer";
    v.setAttribute("role", "dialog");
    v.setAttribute("aria-modal", "true");
    v.setAttribute("aria-label", fig.getAttribute("aria-label") || openLabel);
    var btn = document.createElement("button");
    btn.className = "viewer-close";
    btn.type = "button";
    btn.setAttribute("aria-label", closeLabel);
    btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';
    v.appendChild(clone);
    v.appendChild(btn);
    document.body.appendChild(v);
    var prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function close() {
      v.remove();
      document.body.style.overflow = prevOverflow;
      document.removeEventListener("keydown", onKey);
      fan.focus();
    }
    function onKey(e) { if (e.key === "Escape") close(); }
    btn.addEventListener("click", close);
    v.addEventListener("click", function (e) { if (!clone.contains(e.target)) close(); });
    document.addEventListener("keydown", onKey);
    btn.focus();
  }
  fans.forEach(function (fan) {
    fan.setAttribute("tabindex", "0");
    fan.setAttribute("role", "button");
    fan.setAttribute("aria-label", openLabel);
    fan.addEventListener("click", function () { openViewer(fan); });
    fan.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openViewer(fan); } });
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
      var scroller = show.querySelector(".c-scroll");
      if (scroller && scroller.scrollTo) scroller.scrollTo({ top: 330, behavior: "smooth" });
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
    // No scroll drift: in the fan of three phones the middle one must stay level with the others.
  }
})();
