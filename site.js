// Shared site behaviour — externalised so the CSP can use a strict
// script-src 'self' (no 'unsafe-inline'). Loaded by index.html and faq.html.
//
// i18n: flat dotted keys in /i18n/{lang}.json
//   data-i18n="key"       → textContent
//   data-i18n-html="key"  → innerHTML (first-party trusted copy only)
(function () {
    var SUPPORTED = ["en", "ru", "ja"];
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
    var I18N_CACHE_VER = "v1";
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

        return fetch("/i18n/" + lang + ".json", {
            credentials: "same-origin",
            cache: "force-cache",
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
