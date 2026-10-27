// Theme: automatic, light or dark — the three the app's Appearance setting
// offers. Automatic follows the OS through prefers-color-scheme and needs no
// script at all; this file exists for the reader who chose otherwise.
//
// Loaded synchronously at the top of <head> so a chosen theme is on <html>
// before the first paint — set any later and a reader who picked light on a
// dark OS sees the page flash dark on every navigation. External because the
// CSP allows no inline script. Unlike lang-redirect.js it is on every page,
// /add and /c/… included, so a choice made anywhere holds everywhere.
//
// The choice is `data-theme` on <html>: absent = automatic, "light" / "dark" =
// forced. styles.css and effects.css key their light tokens off exactly that.
(function () {
    var KEY = "construct-theme";
    var MODES = ["auto", "light", "dark"];
    var LABELS = { auto: "AUTO", light: "LIGHT", dark: "DARK" };
    var root = document.documentElement;

    function saved() {
        try {
            var mode = localStorage.getItem(KEY);
            return MODES.indexOf(mode) !== -1 ? mode : "auto";
        } catch (e) {
            return "auto";
        }
    }

    function apply(mode) {
        if (mode === "auto") root.removeAttribute("data-theme");
        else root.setAttribute("data-theme", mode);
    }

    function render(mode) {
        document.querySelectorAll("[data-theme-current]").forEach(function (node) {
            node.textContent = LABELS[mode];
        });
    }

    var mode = saved();
    apply(mode);

    document.addEventListener("DOMContentLoaded", function () {
        render(mode);
        document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                mode = MODES[(MODES.indexOf(mode) + 1) % MODES.length];
                apply(mode);
                render(mode);
                try {
                    if (mode === "auto") localStorage.removeItem(KEY);
                    else localStorage.setItem(KEY, mode);
                } catch (e) {}
            });
        });
    });

    // Another tab changed it: follow, so two open pages never disagree.
    window.addEventListener("storage", function (e) {
        if (e.key !== KEY) return;
        mode = saved();
        apply(mode);
        render(mode);
    });
})();
