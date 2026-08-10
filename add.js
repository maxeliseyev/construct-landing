// Dynamic invite deep-link landing (`/add?invite=…`).
// Externalised so CSP can stay `script-src 'self'` (no inline).
// Loaded with `defer`, so the DOM is ready.
//
// Flow:
// 1. iOS Universal Links may open the app *before* this page loads (AASA path `/add`).
// 2. If the browser still shows this page, fall back to `konstruct://add?invite=…`.
// 3. If the scheme does not open the app, point at TestFlight (no public App Store yet).

const TESTFLIGHT_URL = "https://testflight.apple.com/join/NH3WssFh";

const urlParams = new URLSearchParams(window.location.search);
let invite = urlParams.get("invite");

// Fallback: /add/<payload> (path form) — same shape InviteVerifier accepts.
if (!invite) {
    const pathParts = window.location.pathname
        .split("/")
        .filter((part) => part.length > 0);
    if (pathParts.length >= 2 && pathParts[0] === "add") {
        invite = pathParts[1];
    }
}

// Fragment: #invite=… or bare payload.
if (!invite && window.location.hash) {
    const hash = window.location.hash.replace(/^#/, "");
    invite = hash.startsWith("invite=") ? hash.slice("invite=".length) : hash;
}

const openAppBtn = document.getElementById("openAppButton");
const loading = document.getElementById("loading");
const error = document.getElementById("error");
const message = document.getElementById("message");

function showError(html) {
    if (!error) return;
    error.hidden = false;
    error.innerHTML = html;
}

function setLoading(isLoading) {
    if (loading) loading.hidden = !isLoading;
    if (openAppBtn) openAppBtn.style.display = isLoading ? "none" : "inline-block";
}

if (!invite) {
    if (message) {
        message.textContent = "This invite link is missing its payload.";
    }
    if (openAppBtn) openAppBtn.style.display = "none";
    showError(
        'No invite data in this URL. Ask your contact to share a fresh link from Settings ▸ Copy Contact Link, or scan their QR code.'
    );
} else {
    // Preserve the raw invite token — it is already base64url; do not re-encode.
    const appScheme = "konstruct://add?invite=" + invite;

    if (openAppBtn) {
        openAppBtn.setAttribute("href", appScheme);
    }

    function openInApp(event) {
        if (event) event.preventDefault();
        setLoading(true);
        if (error) error.hidden = true;

        // Custom scheme opens the app when installed. Universal Links already
        // failed if we are rendering this page, so do not re-hit the HTTPS URL.
        window.location.href = appScheme;

        window.setTimeout(() => {
            setLoading(false);
            showError(
                'App not found. Konstruct is in beta — <a href="' +
                    TESTFLIGHT_URL +
                    '">join the TestFlight beta</a>, then open this link again. ' +
                    "You can also paste the link inside the app (Scan ▸ Paste invite link)."
            );
        }, 2000);
    }

    if (openAppBtn) {
        openAppBtn.addEventListener("click", openInApp);
    }

    // Auto-attempt on load for mobile browsers that do not intercept Universal Links
    // (paste into Safari, some in-app webviews, Android until App Links are verified).
    const isMobile =
        /iPhone|iPad|iPod|Android/i.test(navigator.userAgent) ||
        (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
    if (isMobile) {
        openInApp();
    }
}
