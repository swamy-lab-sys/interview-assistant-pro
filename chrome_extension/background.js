chrome.action.onClicked.addListener((tab) => {
    chrome.storage.local.get(['windowId'], (result) => {
        const existingWinId = result.windowId;

        if (existingWinId) {
            // Try to focus existing window
            chrome.windows.update(existingWinId, { focused: true }, () => {
                if (chrome.runtime.lastError) {
                    // Window doesn't exist anymore, create new
                    createWindow();
                }
            });
        } else {
            createWindow();
        }
    });
});

function createWindow() {
    chrome.system.display.getInfo((displays) => {
        // Use primary display
        const primaryDisplay = displays.find(d => d.isPrimary) || displays[0];
        const workArea = primaryDisplay.workArea;

        // Smart Sizing: Don't exceed screen dimensions
        const width = Math.min(600, workArea.width - 50);
        const height = Math.min(800, workArea.height - 50);

        // Exact Center
        const left = Math.round(workArea.left + (workArea.width - width) / 2);
        const top = Math.round(workArea.top + (workArea.height - height) / 2);

        chrome.windows.create({
            url: chrome.runtime.getURL("popup.html"),
            type: "popup",
            width: width,
            height: height,
            left: left,
            top: top,
            focused: true
        }, (newWin) => {
            chrome.storage.local.set({ windowId: newWin.id });
        });
    });
}

// Clean up storage when window is closed manually
chrome.windows.onRemoved.addListener((winId) => {
    chrome.storage.local.get(['windowId'], (result) => {
        if (result.windowId === winId) {
            chrome.storage.local.remove('windowId');
        }
    });
});
