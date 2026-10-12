// First visit to an English page: send the reader to the same page in their
// language. Every language has its own URL (/ru/faq, /tr/, …), built by
// scripts/build-locales.py; English is the unprefixed one.
//
// Loaded synchronously at the top of <head> so English never paints first, and
// external because the CSP allows no inline script. The build leaves it out of
// every non-English page, and it checks <html lang> anyway: someone who
// followed a link to /tr/faq stays there.
//
// The language is the one chosen in the switcher if there ever was one —
// choosing English included, which is what stops the switcher from bouncing a
// reader back — and otherwise the browser's own list, the way site.js detects
// it. No geolocation: a privacy product does not look up its visitors' IPs,
// and a country is not a language.
(function () {
    // Same list and order as SUPPORTED in site.js; the build fails if not.
    var SUPPORTED = ["en", "fr", "tr", "ru", "uk", "hy", "ja"];
    // English path -> suffix after /<lang>. Same pages as PAGES in the build.
    var PAGES = {
        "/": "",
        "/index.html": "",
        "/faq": "/faq",
        "/faq.html": "/faq",
        "/technical": "/technical",
        "/technical.html": "/technical",
        "/roadmap": "/roadmap",
        "/roadmap.html": "/roadmap",
        "/privacy": "/privacy",
        "/privacy.html": "/privacy",
    };

    if (document.documentElement.getAttribute("lang") !== "en") return;
    var path = location.pathname;
    if (!Object.prototype.hasOwnProperty.call(PAGES, path)) return;

    function supported(code) {
        if (!code) return null;
        var base = String(code).toLowerCase().split(/[-_]/)[0];
        return SUPPORTED.indexOf(base) !== -1 ? base : null;
    }

    var lang = null;
    try {
        lang = supported(localStorage.getItem("construct-lang"));
    } catch (e) {}

    if (!lang) {
        var list = navigator.languages && navigator.languages.length
            ? navigator.languages
            : [navigator.language || navigator.userLanguage];
        for (var i = 0; i < list.length && !lang; i++) lang = supported(list[i]);
    }

    if (!lang || lang === "en") return;
    location.replace("/" + lang + PAGES[path] + location.search + location.hash);
})();
