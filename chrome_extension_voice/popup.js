// Popup script for Voice Assistant Extension

const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');

// Check server status on popup open
checkServerStatus();

// Button event listeners
document.getElementById('openVoiceTab').addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'openVoice', mode: 'tab' });
    window.close();
});

document.getElementById('openVoicePopup').addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'openVoice', mode: 'popup' });
    window.close();
});

document.getElementById('openMain').addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'openMain' });
    window.close();
});

// Check if server is running
function checkServerStatus() {
    chrome.runtime.sendMessage({ action: 'checkServer' }, (response) => {
        if (response && response.running) {
            statusDot.classList.remove('offline');
            statusText.textContent = 'Server Online';
        } else {
            statusDot.classList.add('offline');
            statusText.textContent = 'Server Offline';
            showOfflineWarning();
        }
    });
}

// Show warning if server is offline
function showOfflineWarning() {
    const warning = document.createElement('div');
    warning.style.cssText = `
    background: rgba(248, 113, 113, 0.2);
    border: 1px solid rgba(248, 113, 113, 0.5);
    padding: 12px;
    border-radius: 8px;
    margin-top: 12px;
    font-size: 12px;
    text-align: center;
  `;
    warning.innerHTML = `
    <strong>⚠️ Server Not Running</strong><br>
    Start server: <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px;">python3 web/server.py</code>
  `;
    document.querySelector('.content').appendChild(warning);
}

// Refresh status every 3 seconds while popup is open
setInterval(checkServerStatus, 3000);
