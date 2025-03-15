const { app, BrowserWindow, ipcMain } = require('electron');

let mainWindow;

app.whenReady().then(() => {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false // Required for IPC communication
        }
    });

    mainWindow.loadFile('navigate.html');
});

// Handle navigation requests from the renderer process
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
