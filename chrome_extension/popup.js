document.addEventListener('DOMContentLoaded', function () {
    console.log("Popup script loaded.");

    function toggleQR() {
        const el = document.getElementById('qrOverlay');
        if (!el) return;
        const current = getComputedStyle(el).display;
        el.style.display = current === 'flex' ? 'none' : 'flex';
    }

    const btnMobile = document.getElementById('btnMobile');
    if (btnMobile) {
        btnMobile.addEventListener('click', toggleQR);
    }

    const btnBack = document.getElementById('btnBack');
    if (btnBack) {
        btnBack.addEventListener('click', toggleQR);
    }

    const btnClose = document.getElementById('btnClose');
    if (btnClose) {
        btnClose.addEventListener('click', function () {
            window.close();
        });
    }
});
