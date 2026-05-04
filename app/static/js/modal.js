const modal = document.getElementById("sessionModal");

if (modal) {

    const countdownEl = document.getElementById("countdown");
    const stayBtn = document.getElementById("stayBtn");
    const logoutBtn = document.getElementById("logoutBtn");
    const logoutForm = document.getElementById("logoutForm");

    const WARNING_TIME = 20;

    let remaining = null;
    let countdownInterval = null;
    let syncInterval = null;
    let warningShown = false;
    let loggingOut = false;

    const STATUS_URL = "/session_status";
    const REFRESH_URL = "/refresh_session";
    const LOGOUT_URL = "/auto_logout";
    const EXPIRED_URL = "/session_expired/";

    function stopIntervals() {
        if (countdownInterval) clearInterval(countdownInterval);
        if (syncInterval) clearInterval(syncInterval);
        countdownInterval = null;
        syncInterval = null;
    }

    function showModal() {
        if (!warningShown) {
            warningShown = true;
            modal.classList.add("active");
        }
    }

    function hideModal() {
        warningShown = false;
        modal.classList.remove("active");
    }

    function updateCountdown() {
        if (remaining === null || loggingOut) return;

        const seconds = Math.max(0, Math.ceil(remaining));
        countdownEl.textContent = seconds;

        if (seconds <= 0) {
            autoLogout();
        } else if (seconds <= WARNING_TIME) {
            showModal();
        } else {
            hideModal();
        }
    }

    async function syncSession() {
        try {
            const res = await fetch(STATUS_URL, {
                method: "GET",
                credentials: "same-origin",
                cache: "no-store"
            });

            if (!res.ok) return;

            const data = await res.json();
            remaining = Number(data.remaining);

            updateCountdown();

        } catch (err) {
            console.error("Error sync session:", err);
        }
    }

    async function getCSRFToken() {
        try {
            const res = await fetch("/csrf-token", {
                method: "GET",
                credentials: "same-origin",
                cache: "no-store"
            });

            if (!res.ok) return null;

            const data = await res.json();
            return data.csrf_token;

        } catch (err) {
            console.error("Error obteniendo CSRF:", err);
            return null;
        }
    }

    async function refreshSession() {
        try {
            const csrfToken = await getCSRFToken();

            const res = await fetch(REFRESH_URL, {
                method: "POST",
                credentials: "same-origin",
                cache: "no-store",
                keepalive: true,
                headers: csrfToken ? {
                    "X-CSRFToken": csrfToken
                } : {}
            });

            if (res.ok) {
                hideModal();
                await syncSession();
            }

        } catch (err) {
            console.error("Error refreshing session:", err);
        }
    }


    async function autoLogout() {
    if (loggingOut) return;
    loggingOut = true;

    stopIntervals();
    hideModal();

    const csrfToken = logoutForm?.querySelector('input[name="csrf_token"]')?.value;

    try {
        await fetch(LOGOUT_URL, {
            method: "POST",
            credentials: "same-origin",
            cache: "no-store",
            headers: csrfToken ? {
                "X-CSRFToken": csrfToken
            } : {}
        });
    } catch (err) {
        console.warn("Error en autoLogout:", err);
    }

    window.location.href = EXPIRED_URL;
    }

    function manualLogout() {
        if (loggingOut) return;
        loggingOut = true;

        stopIntervals();
        hideModal();

        if (logoutForm) {
            logoutForm.submit();
            return;
        }

        window.location.href = "/signin/";
    }

    stayBtn?.addEventListener("click", (e) => {
        e.preventDefault();
        refreshSession();
    });

    logoutBtn?.addEventListener("click", (e) => {
        e.preventDefault();
        manualLogout();
    });

    document.addEventListener("visibilitychange", () => {
        if (!document.hidden && !loggingOut) {
            syncSession();
        }
    });

    window.addEventListener("focus", () => {
        if (!loggingOut) syncSession();
    });

    window.addEventListener("pageshow", () => {
        if (!loggingOut) syncSession();
    });

    syncSession();

    countdownInterval = setInterval(() => {
        if (remaining !== null && !loggingOut) {
            remaining -= 1;
            updateCountdown();
        }
    }, 1000);

    syncInterval = setInterval(() => {
        if (!loggingOut) syncSession();
    }, 5000);

    window.addEventListener("beforeunload", () => {
        stopIntervals();
    });
}
