const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { inviokeScript } = require('./utils/invoke');

let mainWindow;

app.whenReady().then(() => {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false, // Required for IPC communication
        }
    });

    mainWindow.loadFile('navigate.html');
});

// Handle query submission by calling the helper function
ipcMain.on('run-python-query', (event, query) => {
    inviokeScript('query.py', {"query":query}, event);
});

// Handle navigation requests
ipcMain.on('navigate-to-upload', () => {
    mainWindow.loadFile('uploadcsv.html');
});

ipcMain.on('navigate-to-query', () => {
    mainWindow.loadFile('query.html');
});

ipcMain.on('navigate-to-home', () => {
    mainWindow.loadFile('navigate.html');
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
