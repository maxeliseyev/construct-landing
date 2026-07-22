// Shared site behaviour — externalised so the CSP can use a strict
// script-src 'self' (no 'unsafe-inline'). Loaded by index.html and faq.html.
(function () {
    function setLang(lang) {
        var el = document.documentElement;
        el.setAttribute("data-lang", lang);
        el.setAttribute("lang", lang);
        try {
            localStorage.setItem("construct-lang", lang);
        } catch (e) {}
        document.querySelectorAll("[data-lang-btn]").forEach(function (btn) {
            btn.classList.toggle("active", btn.dataset.langBtn === lang);
        });
        // Optional per-page title switch via data-title-en / data-title-ru on <html>.
        var t =
            lang === "ru"
                ? el.getAttribute("data-title-ru")
                : el.getAttribute("data-title-en");
        if (t) document.title = t;
    }

    function initLang() {
        var saved = localStorage.getItem("construct-lang");
        var lang =
            saved === "en" || saved === "ru"
                ? saved
                : (navigator.language || "").toLowerCase().startsWith("ru")
                  ? "ru"
                  : "en";
        setLang(lang);
    }

    function copyAddr(el) {
        if (!navigator.clipboard) return;
        navigator.clipboard.writeText(el.textContent.trim()).then(function () {
            el.classList.add("copied");
            setTimeout(function () {
                el.classList.remove("copied");
            }, 1200);
        });
    }

    function wire() {
        document.querySelectorAll("[data-lang-btn]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                setLang(btn.dataset.langBtn);
            });
        });
        document.querySelectorAll(".addr").forEach(function (a) {
            a.addEventListener("click", function () {
                copyAddr(a);
            });
        });
    }

    initLang();
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", wire);
    } else {
        wire();
    }
})();
