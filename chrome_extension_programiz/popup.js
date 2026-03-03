document.addEventListener('DOMContentLoaded', () => {
  // Buttons
  document.getElementById('btn-start').addEventListener('click', () => {
    sendCommand('start-solving');
    window.close(); // Close popup so user sees the action
  });

  document.getElementById('btn-pause').addEventListener('click', () => {
    sendCommand('trigger-pause');
  });

  document.getElementById('btn-stop').addEventListener('click', () => {
    sendCommand('trigger-stop');
  });

  // WPM Slider
  const wpmSlider = document.getElementById('wpmSlider');
  const wpmValue = document.getElementById('wpmValue');

  if (wpmSlider && wpmValue) {
    // Load saved WPM value
    chrome.storage.sync.get({ wpm: 20 }, (data) => {
      wpmSlider.value = data.wpm;
      wpmValue.textContent = data.wpm + ' WPM';
    });

    // Update on slider change
    wpmSlider.addEventListener('input', () => {
      const val = parseInt(wpmSlider.value);
      wpmValue.textContent = val + ' WPM';
      chrome.storage.sync.set({ wpm: val });
      console.log('WPM set to:', val);
    });
  }
});

function sendCommand(command) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs.length === 0) return;

    // Send to content script
    chrome.tabs.sendMessage(tabs[0].id, {
      type: 'EXTENSION_COMMAND',
      command: command
    }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('Could not send command:', chrome.runtime.lastError);
      } else {
        console.log('Command sent:', command);
      }
    });
  });
}
