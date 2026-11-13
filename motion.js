/* arranko.app motion: scroll reveals, the kcal counter, macro bars and a gentle parallax.
   Runs only when <head> switched motion on (html.motion). No libraries, no tracking. */
(function () {
  var d = document.documentElement;
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

  // The example estimate: count the calories up and fill the macro bars once the card has arrived.
  var card = document.querySelector(".estimate");
  if (card) {
    var splashing = d.classList.contains("splashing");
    var start = (splashing ? 3050 : 150) + 900;
    var num = card.querySelector("[data-count]");
    setTimeout(function () {
      card.classList.add("filled");
      if (!num) return;
      var target = parseInt(num.getAttribute("data-count"), 10), t0 = null, dur = 1100;
      function step(t) {
        if (t0 === null) t0 = t;
        var p = Math.min(1, (t - t0) / dur), eased = 1 - Math.pow(1 - p, 3);
        num.textContent = Math.round(target * eased);
        if (p < 1) requestAnimationFrame(step);
      }
      num.textContent = "0";
      requestAnimationFrame(step);
    }, start);

    // Parallax on wide screens: the card drifts a little slower than the page.
    var wide = window.matchMedia("(min-width: 901px)");
    var ticking = false;
    window.addEventListener("scroll", function () {
      if (!wide.matches || ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        var y = Math.min(window.scrollY, 700) * 0.12;
        card.style.translate = "0 " + y + "px";
        ticking = false;
      });
    }, { passive: true });
  }
})();
