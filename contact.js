// Contact deep-link handling — externalised so the CSP can use a strict
// script-src 'self' (no 'unsafe-inline'). Loaded with `defer`, so the DOM is ready.

// Parse userId from the path first: /c/{userId}
let userId = null;
const pathParts = window.location.pathname
    .split("/")
    .filter((part) => part.length > 0);
if (pathParts.length >= 2 && pathParts[0] === "c") {
    userId = pathParts[1];
}

// Fallback to query parameter if not in path
const urlParams = new URLSearchParams(window.location.search);
if (!userId) {
    userId = urlParams.get("userId");
}
const username = urlParams.get("username");

// Update UI
if (username) {
    document.getElementById("username").textContent = "@" + username;
} else {
    document.getElementById("username").style.display = "none";
}

// Validate userId
if (!userId) {
    const errorEl = document.getElementById("error");
    errorEl.hidden = false;
    errorEl.textContent = "Error: User ID not specified";
    document.getElementById("openAppButton").style.display = "none";
}

// Universal link for iOS
const universalLink = window.location.href;

// Custom URL scheme fallback (if needed in future)
const appScheme =
    "konstruct://contact?userId=" +
    encodeURIComponent(userId || "") +
    "&username=" +
    encodeURIComponent(username || "");

function openInApp(event) {
    event.preventDefault();

    const openAppBtn = document.getElementById("openAppButton");
    const loading = document.getElementById("loading");
    const error = document.getElementById("error");

    openAppBtn.style.display = "none";
    loading.hidden = false;
    error.hidden = true;

    // Try universal link first (for iOS) — handled by iOS if the app is installed
    window.location.href = universalLink;

    // Fallback: try custom URL scheme
    setTimeout(() => {
        window.location.href = appScheme;
    }, 500);

    // If still not opened after 2 seconds, show error. Konstruct has no public
    // App Store release yet — point to the TestFlight beta instead.
    setTimeout(() => {
        loading.hidden = true;
        error.hidden = false;
        error.innerHTML =
            'App not found. Konstruct Messenger is currently in beta — <a href="https://testflight.apple.com/join/NH3WssFh">join the TestFlight beta</a> to install it.';
        openAppBtn.style.display = "inline-block";
    }, 2000);
}

const openAppButton = document.getElementById("openAppButton");
if (openAppButton) openAppButton.addEventListener("click", openInApp);
