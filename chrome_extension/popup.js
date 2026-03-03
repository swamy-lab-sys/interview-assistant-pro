document.addEventListener('DOMContentLoaded', function () {
    console.log("Popup script loaded.");

    function toggleQR() {
        const el = document.getElementById('qrOverlay');
        const img = document.getElementById('qrImage');
        if (!el || !img) return;

        const current = getComputedStyle(el).display;

        if (current !== 'flex') {
            el.style.display = 'flex';

            // Set a valid placeholder immediately
            if (!img.src || img.src.endsWith('.html') || img.src === window.location.href) {
                img.src = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=http://localhost:8000";
            }

            // Fetch real IP
            fetch('http://localhost:8000/api/ip')
                .then(r => r.json())
                .then(d => {
                    if (d.ip) {
                        const url = `http://${d.ip}:8000`;
                        img.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(url)}`;
                        document.getElementById('qrUrl').textContent = url;
                    }
                })
                .catch(e => {
                    console.error("Failed to get IP:", e);
                    document.getElementById('qrUrl').textContent = "Connection Failed (Using Localhost)";
                });
        } else {
            el.style.display = 'none';
        }
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
