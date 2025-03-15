document.addEventListener('DOMContentLoaded', () => {
    document.body.style.backgroundColor = '#f5f5f5';
});

const { ipcRenderer } = require('electron');

// Function to open the file dialog
function uploadCSV() {
    ipcRenderer.send('open-file-dialog'); // Request to open the file dialog
}

// Listener to update the status message after uploading
ipcRenderer.on('upload-status', (event, message) => {
    document.getElementById('status').innerText = message;
});

// Navigation back to home
function goBack() {
    ipcRenderer.send('navigate-to-home');
}
