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
    var ring = clone.querySelector(".t-ring"); if (ring) ring.setAttribute("stroke-dashoffset", "220.60");
    var bars = clone.querySelectorAll(".t-bar"), widths = ["68.8%", "19.1%", "23.8%"];
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

  // Phones on narrow screens: a swipe carousel. The phone nearest the centre grows to full size,
  // the others shrink and fade; dots show and jump to each phone. Starts on the middle phone.
  var strip = document.querySelector(".hero-fan");
  var narrow = window.matchMedia("(max-width: 760px)");
  if (strip && fans.length) {
    var dots = document.createElement("div");
    dots.className = "fan-dots";
    var dotLabel = d.lang === "es" ? "Pantalla %n de 3" : "Screen %n of 3";
    fans.forEach(function (fan, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-label", dotLabel.replace("%n", i + 1));
      b.addEventListener("click", function () { centre(i, true); });
      dots.appendChild(b);
    });
    strip.parentNode.insertBefore(dots, strip.nextSibling);
    function centre(i, smooth) {
      var fan = fans[i];
      var left = fan.offsetLeft + fan.offsetWidth / 2 - strip.clientWidth / 2;
      strip.scrollTo({ left: left, behavior: smooth ? "smooth" : "auto" });
    }
    var raf = 0;
    function update() {
      raf = 0;
      if (!narrow.matches) {
        fans.forEach(function (f) { f.style.removeProperty("--z"); f.style.removeProperty("--o"); });
        return;
      }
      var mid = strip.scrollLeft + strip.clientWidth / 2, best = 0, bestDist = Infinity;
      fans.forEach(function (f, i) {
        var offset = f.offsetLeft + f.offsetWidth / 2 - mid;
        var dist = Math.abs(offset);
        var k = Math.min(1, dist / f.offsetWidth);
        f.style.setProperty("--z", (1 - 0.16 * k).toFixed(3));
        f.style.setProperty("--o", (1 - 0.45 * k).toFixed(3));
        // Side phones lean outwards like the desktop fan (left one to the left, right one to the right);
        // the phone in the centre (or nearly) stands straight.
        var lean = k < 0.15 ? 0 : (k - 0.15) / 0.85;
        f.style.setProperty("--r", ((offset < 0 ? -1 : 1) * 10 * lean).toFixed(2) + "deg");
        if (dist < bestDist) { bestDist = dist; best = i; }
      });
      dots.querySelectorAll("button").forEach(function (b, i) { b.setAttribute("aria-current", i === best ? "true" : "false"); });
    }
    strip.addEventListener("scroll", function () { if (!raf) raf = requestAnimationFrame(update); }, { passive: true });
    strip.addEventListener("scrollend", update);
    // Re-centre only when the width really changes (a phone's address bar showing or hiding also
    // fires "resize", and must not move the carousel).
    var lastWidth = window.innerWidth;
    window.addEventListener("resize", function () {
      if (window.innerWidth !== lastWidth) { lastWidth = window.innerWidth; if (narrow.matches) centre(1, false); }
      update();
    });
    window.addEventListener("load", function () { if (narrow.matches && strip.scrollLeft === 0) centre(1, false); update(); });
    if (narrow.matches) centre(1, false);
    update();
  }

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
