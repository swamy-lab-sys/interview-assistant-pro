// Background service worker for Voice Assistant Extension

const VOICE_URL = 'http://localhost:8000/voice';
const MAIN_URL = 'http://localhost:8000/';

// Listen for extension icon click
chrome.action.onClicked.addListener(() => {
    openVoiceAssistant('tab');
});

// Listen for keyboard commands
chrome.commands.onCommand.addListener((command) => {
    if (command === 'open-voice-mode') {
        openVoiceAssistant('tab');
    } else if (command === 'open-voice-popup') {
        openVoiceAssistant('popup');
    }
});

// Open voice assistant in different modes
function openVoiceAssistant(mode) {
    if (mode === 'popup') {
        // Small popup window (optimized for side-by-side with interview)
        chrome.windows.create({
            url: VOICE_URL,
            type: 'popup',
            width: 500,
            height: 800,
            left: screen.width - 520,
            top: 0
        });
    } else {
        // Full tab
        chrome.tabs.create({
            url: VOICE_URL,
            active: true
        });
    }
}

// Message listener for communication with popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'openVoice') {
        openVoiceAssistant(request.mode || 'tab');
        sendResponse({ success: true });
    } else if (request.action === 'openMain') {
        chrome.tabs.create({ url: MAIN_URL });
        sendResponse({ success: true });
    } else if (request.action === 'checkServer') {
        // Check if server is running
        fetch(MAIN_URL)
            .then(() => sendResponse({ running: true }))
            .catch(() => sendResponse({ running: false }));
        return true; // Keep channel open for async response
    }
});

// Install/Update handler
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('Interview Voice Assistant installed!');
        // Show welcome page
        chrome.tabs.create({
            url: VOICE_URL
        });
    } else if (details.reason === 'update') {
        console.log('Interview Voice Assistant updated to version', chrome.runtime.getManifest().version);
    }
});
