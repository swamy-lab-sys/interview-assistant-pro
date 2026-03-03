// Background Service Worker
// Handles HTTP requests to Localhost to bypass Mixed Content restrictions on HTTPS sites

console.log('Interview Assistant Background Service Started');

// Listen for messages from Content Script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'SOLVE_PROBLEM_PROXY') {
        handleSolveRequest(request.payload, sendResponse);
        return true; // Keep message channel open for async response
    }
    if (request.type === 'FETCH_SOLUTION_BY_INDEX') {
        handleFetchSolutionByIndex(request.index, sendResponse);
        return true;
    }
    if (request.type === 'CONTROL_START') {
        handleControlStart(sendResponse);
        return true;
    }
});

async function handleControlStart(sendResponse) {
    try {
        console.log('[BG] Triggering control/start...');
        await fetch('http://localhost:8000/api/control/start', { method: 'POST' });
        sendResponse({ success: true });
    } catch (err) {
        console.error('[BG] control/start failed:', err);
        sendResponse({ success: false, error: err.message });
    }
}

async function handleFetchSolutionByIndex(index, sendResponse) {
    const url = `http://localhost:8000/api/get_answer_by_index?index=${index}`;
    console.log(`[BG] Proxying fetch request for index #${index} -> ${url}`);

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Server returned ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        console.log('[BG] Success:', data);
        sendResponse({ success: true, data: data });
    } catch (error) {
        console.error('[BG] Fetch index failed:', error);
        // Retry once after small delay
        try {
            console.log('[BG] Retrying fetch...');
            await new Promise(r => setTimeout(r, 500));
            const retryResp = await fetch(url);
            const retryData = await retryResp.json();
            sendResponse({ success: true, data: retryData });
        } catch (retryError) {
            console.error('[BG] Retry also failed:', retryError);
            sendResponse({ success: false, error: error.message });
        }
    }
}

async function handleSolveRequest(payload, sendResponse) {
    try {
        console.log('Proxying solve request to localhost:', payload.url);

        // Call Python Server
        const response = await fetch('http://localhost:8000/api/solve_problem', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Solution received:', data);
        sendResponse({ success: true, data: data });

    } catch (error) {
        console.error('Solve request failed:', error);
        sendResponse({ success: false, error: error.message });
    }
}

// Popup window management
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
