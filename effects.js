(function () {
  "use strict";

  if (!document.body.classList.contains("landing")) return;

  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var GLYPHS = ">$#@%&*+=\\|~^:;[]{}0123456789";

  function getTextTarget(el) {
    var lang = document.documentElement.getAttribute("data-lang") || "en";
    var inner = el.querySelector("." + lang);
    return inner || el;
  }

  function scramble(el, durationMs) {
    if (reducedMotion || el.dataset.scrambling === "1") return;

    var target = getTextTarget(el);
    var original = target.dataset.originalText || target.textContent;
    target.dataset.originalText = original;
    el.dataset.scrambling = "1";
    target.classList.add("is-scrambling");

    var start = performance.now();
    var len = original.length;

    function tick(now) {
      var elapsed = now - start;
      var progress = Math.min(elapsed / durationMs, 1);
      var revealCount = Math.floor(progress * len);
      var out = "";

      for (var i = 0; i < len; i++) {
        if (i < revealCount) {
          out += original[i];
        } else if (original[i] === " ") {
          out += " ";
        } else {
          out += GLYPHS[(Math.random() * GLYPHS.length) | 0];
        }
      }

      target.textContent = out;

      if (progress < 1) {
        requestAnimationFrame(tick);
      } else {
        target.textContent = original;
        target.classList.remove("is-scrambling");
        el.dataset.scrambling = "0";
      }
    }

    requestAnimationFrame(tick);
  }

  function bindCorrupt(selector) {
    document.querySelectorAll(selector).forEach(function (el) {
      el.classList.add("corrupt-target");
      el.addEventListener("mouseenter", function () {
        scramble(el, 420);
      });
    });
  }

  bindCorrupt(".landing .badge");
  bindCorrupt(".landing .lang-switcher button");
  bindCorrupt(".landing main section:last-of-type a");

  if (!reducedMotion && "IntersectionObserver" in window) {
    var headings = document.querySelectorAll(".landing main h2");
    var seen = new WeakSet();
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting && !seen.has(entry.target)) {
            seen.add(entry.target);
            entry.target.classList.add("in-view");
            window.setTimeout(function () {
              entry.target.classList.remove("in-view");
            }, 200);
          }
        });
      },
      { threshold: 0.6 },
    );
    headings.forEach(function (h) {
      observer.observe(h);
    });
  }
})();
