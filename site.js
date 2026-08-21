// Shared site behaviour — externalised so the CSP can use a strict
// script-src 'self' (no 'unsafe-inline'). Loaded by index.html and faq.html.
//
// i18n: flat dotted keys in /i18n/{lang}.json
//   data-i18n="key"       → textContent
//   data-i18n-html="key"  → innerHTML (first-party trusted copy only)
(function () {
    // "ja" is intentionally absent: ja.json is machine-drafted and has not been
    // reviewed by a Japanese speaker. The translations are kept in i18n/ja.json —
    // re-add "ja" here and restore the switcher entries once they are checked.
    var SUPPORTED = ["en", "ru"];
    var LABELS = {
        en: "EN",
        ru: "RU",
        ja: "JA",
    };
    var NAMES = {
        en: "English",
        ru: "Русский",
        ja: "日本語",
    };

    // Bump when JSON shape or cache semantics change.
    // Content hash of i18n/{en,ru,ja}.json — NOT hand-maintained. The sessionStorage
// copy is keyed by this alone, so a stale dictionary otherwise survives a deploy:
// a cached dict without the new keys leaves the switcher reading RU while every
// string falls back to the English in the markup, because applyI18n skips a
// missing value. That happened twice — once on the privacy.* extraction, and
// again the very next day on the delivery-status keys, with a comment sitting
// right here telling me to bump it. `scripts/check-i18n.py` now computes the
// expected value and fails if this line disagrees, so it cannot be forgotten.
var I18N_CACHE_VER = "3fae0c6bd0";
    var dictCache = Object.create(null);
    var currentLang = "en";
    var currentDict = null;
    var readyResolve;
    var ready = new Promise(function (resolve) {
        readyResolve = resolve;
    });

    function isSupported(lang) {
        return SUPPORTED.indexOf(lang) !== -1;
    }

    function normalizeLang(code) {
        if (!code) return null;
        var base = String(code).toLowerCase().split(/[-_]/)[0];
        return isSupported(base) ? base : null;
    }

    function detectLang() {
        try {
            var saved = localStorage.getItem("construct-lang");
            if (isSupported(saved)) return saved;
        } catch (e) {}

        var candidates = [];
        if (navigator.languages && navigator.languages.length) {
            for (var i = 0; i < navigator.languages.length; i++) {
                candidates.push(navigator.languages[i]);
            }
        } else if (navigator.language) {
            candidates.push(navigator.language);
        } else if (navigator.userLanguage) {
            candidates.push(navigator.userLanguage);
        }

        for (var j = 0; j < candidates.length; j++) {
            var hit = normalizeLang(candidates[j]);
            if (hit) return hit;
        }
        return "en";
    }

    function cacheKey(lang) {
        return "construct-i18n-" + I18N_CACHE_VER + "-" + lang;
    }

    function loadDict(lang) {
        if (!isSupported(lang)) lang = "en";
        if (dictCache[lang]) return Promise.resolve(dictCache[lang]);

        try {
            var raw = sessionStorage.getItem(cacheKey(lang));
            if (raw) {
                var parsed = JSON.parse(raw);
                if (parsed && typeof parsed === "object") {
                    dictCache[lang] = parsed;
                    return Promise.resolve(parsed);
                }
            }
        } catch (e) {}

        // The version goes in the URL, not just in the sessionStorage key. Without
        // it this fetch is subject to `stale-while-revalidate=86400` and a browser
        // hands back a day-old dictionary instantly — which then gets stored under
        // the NEW cache key, so the marker moved and the words did not. That is how
        // the dropped Signal section stayed on screen after it was gone from the
        // repo, from the deploy, and from the live JSON. A changed URL cannot hit a
        // cache entry, so this is a mechanism rather than a request to be careful.
        return fetch("/i18n/" + lang + ".json?v=" + I18N_CACHE_VER, {
            credentials: "same-origin",
            cache: "default",
        })
            .then(function (res) {
                if (!res.ok) throw new Error("i18n " + lang + " HTTP " + res.status);
                return res.json();
            })
            .then(function (dict) {
                dictCache[lang] = dict;
                try {
                    sessionStorage.setItem(cacheKey(lang), JSON.stringify(dict));
                } catch (e) {}
                return dict;
            });
    }

    function pageNamespace() {
        var ns = document.documentElement.getAttribute("data-i18n-page");
        return ns || null;
    }

    function applyI18n(dict) {
        if (!dict) return;

        document.querySelectorAll("[data-i18n]").forEach(function (el) {
            var key = el.getAttribute("data-i18n");
            if (!key) return;
            var val = dict[key];
            if (val == null) return;
            el.textContent = val;
            // A .glitch-text draws its RGB-split layers from `content:
            // attr(data-text)`. Translate the label without moving the
            // attribute and the ghost layers keep saying the previous language,
            // which is visible the moment the element glitches. Here is the one
            // place that knows the new string.
            if (el.hasAttribute("data-text")) el.setAttribute("data-text", val);
            if (el.dataset) delete el.dataset.originalText;
        });

        document.querySelectorAll("[data-i18n-html]").forEach(function (el) {
            var key = el.getAttribute("data-i18n-html");
            if (!key) return;
            var val = dict[key];
            if (val == null) return;
            el.innerHTML = val;
            if (el.dataset) delete el.dataset.originalText;
        });

        // Title: prefer page-scoped meta key, then legacy data-title-* attrs.
        var ns = pageNamespace();
        var titleKey = ns ? ns + ".meta.title" : null;
        var t = titleKey && dict[titleKey] != null ? dict[titleKey] : null;
        if (!t) {
            var html = document.documentElement;
            t =
                html.getAttribute("data-title-" + currentLang) ||
                html.getAttribute("data-title-en");
        }
        if (t) document.title = t;

        currentDict = dict;
    }

    function updateSwitcherChrome(lang) {
        document.querySelectorAll("[data-lang-btn]").forEach(function (btn) {
            var active = btn.dataset.langBtn === lang;
            btn.classList.toggle("active", active);
            btn.setAttribute("aria-selected", active ? "true" : "false");
        });
        document.querySelectorAll("[data-lang-current]").forEach(function (node) {
            node.textContent = LABELS[lang] || lang.toUpperCase();
        });
    }

    function setDocumentLang(lang) {
        var el = document.documentElement;
        el.setAttribute("data-lang", lang);
        el.setAttribute("lang", lang);
        try {
            localStorage.setItem("construct-lang", lang);
        } catch (e) {}
        updateSwitcherChrome(lang);
    }

    function setLang(lang) {
        if (!isSupported(lang)) lang = "en";
        currentLang = lang;
        setDocumentLang(lang);

        return loadDict(lang)
            .then(function (dict) {
                applyI18n(dict);
                try {
                    document.dispatchEvent(
                        new CustomEvent("construct:langchange", {
                            detail: { lang: lang },
                        })
                    );
                } catch (e) {}
                return dict;
            })
            .catch(function () {
                // Keep EN fallback already in the DOM; chrome still reflects intent.
                try {
                    document.dispatchEvent(
                        new CustomEvent("construct:langchange", {
                            detail: { lang: lang },
                        })
                    );
                } catch (e) {}
            });
    }

    function t(key) {
        if (currentDict && currentDict[key] != null) return currentDict[key];
        return null;
    }

    function closeMenus(except) {
        document.querySelectorAll(".lang-switcher").forEach(function (sw) {
            if (except && sw === except) return;
            sw.classList.remove("is-open");
            var trigger = sw.querySelector("[data-lang-trigger]");
            if (trigger) trigger.setAttribute("aria-expanded", "false");
            var menu = sw.querySelector(".lang-menu");
            if (menu) menu.hidden = true;
        });
    }

    function wireSwitcher(sw) {
        var trigger = sw.querySelector("[data-lang-trigger]");
        var menu = sw.querySelector(".lang-menu");
        if (!trigger || !menu) return;

        trigger.addEventListener("click", function (e) {
            e.stopPropagation();
            var open = !sw.classList.contains("is-open");
            closeMenus();
            if (open) {
                sw.classList.add("is-open");
                trigger.setAttribute("aria-expanded", "true");
                menu.hidden = false;
            }
        });

        menu.querySelectorAll("[data-lang-btn]").forEach(function (btn) {
            btn.addEventListener("click", function (e) {
                e.stopPropagation();
                setLang(btn.dataset.langBtn);
                closeMenus();
            });
        });
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
        document.querySelectorAll(".lang-switcher").forEach(wireSwitcher);

        document.querySelectorAll("[data-lang-btn]").forEach(function (btn) {
            if (btn.closest(".lang-menu")) return;
            if (btn.hasAttribute("data-lang-trigger")) return;
            btn.addEventListener("click", function () {
                setLang(btn.dataset.langBtn);
            });
        });

        document.addEventListener("click", function () {
            closeMenus();
        });
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") closeMenus();
        });

        document.querySelectorAll(".addr").forEach(function (a) {
            a.addEventListener("click", function () {
                copyAddr(a);
            });
        });

        wireBurger();
    }

    // Mobile section menu. The panel is the same <ul> the desktop bar shows, so
    // there is one list of sections and one place to add to it.
    function wireBurger() {
        var burger = document.getElementById("navBurger");
        var panel = document.getElementById("navPanel");
        if (!burger || !panel) return;

        function setOpen(open) {
            burger.setAttribute("aria-expanded", open ? "true" : "false");
            panel.classList.toggle("is-open", open);
            // Locking the body is what stops the page scrolling behind the panel;
            // without it a swipe moves the article under an opaque overlay and the
            // reader loses their place for no visible reason.
            document.body.classList.toggle("nav-open", open);
            if (open) {
                var first = panel.querySelector(".nav-links a");
                if (first) first.focus();
            }
        }

        burger.addEventListener("click", function (e) {
            e.stopPropagation();
            setOpen(burger.getAttribute("aria-expanded") !== "true");
        });

        // Following a link must close the panel: on a same-page anchor the browser
        // does not navigate, so an overlay left open would swallow the destination.
        panel.addEventListener("click", function (e) {
            // Only section links dismiss. The language control lives in here
            // too, and closing the panel out from under its dropdown would
            // make the language impossible to change on a phone.
            if (e.target.closest(".nav-links a")) setOpen(false);
            else e.stopPropagation();
        });

        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && burger.getAttribute("aria-expanded") === "true") {
                setOpen(false);
                burger.focus();
            }
        });

        // Resizing past the breakpoint leaves `is-open` on an element that is no
        // longer a panel — the desktop bar would inherit a hidden state it has no
        // control to undo.
        var mq = window.matchMedia("(min-width: 641px)");
        var onChange = function (ev) {
            if (ev.matches) setOpen(false);
        };
        if (mq.addEventListener) mq.addEventListener("change", onChange);
        else if (mq.addListener) mq.addListener(onChange);
    }

    // Sync chrome ASAP; dictionary apply is async.
    currentLang = detectLang();
    setDocumentLang(currentLang);

    setLang(currentLang).then(function () {
        readyResolve(currentLang);
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", wire);
    } else {
        wire();
    }

    window.ConstructLang = {
        set: setLang,
        detect: detectLang,
        t: t,
        ready: ready,
        supported: SUPPORTED.slice(),
        labels: LABELS,
        names: NAMES,
        get lang() {
            return currentLang;
        },
    };
})();
