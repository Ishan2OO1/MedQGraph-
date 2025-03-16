const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const fs = require('fs');
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

// Open file dialog to select CSV file
ipcMain.on('open-file-dialog', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openFile'],
        filters: [{ name: 'CSV Files', extensions: ['csv'] }]
    });

    if (result.canceled) {
        mainWindow.webContents.send('upload-status', 'File selection was canceled.');
    } else {
        const filePath = result.filePaths[0]; // Get selected file path
        mainWindow.webContents.send('upload-status', 'CSV file selected.');
        ipcMain.emit('process-csv', null, filePath); // Process the selected file
    }
});

// Handle CSV upload and save it to a folder
ipcMain.on('process-csv', (event, filePath) => {
    const uploadFolder = path.join(__dirname, 'uploads'); // Specify your folder here

    // Ensure the folder exists
    if (!fs.existsSync(uploadFolder)) {
        console.log('Creating upload folder...');
        fs.mkdirSync(uploadFolder); // Create folder if it doesn't exist
    }

    const fileExtension = path.extname(filePath); // Get file extension
    const timestamp = Date.now(); // Unique timestamp for file name
    const originalFileName = path.basename(filePath, fileExtension); // Get original file name without extension
    const newFileName = `${originalFileName}-${timestamp}${fileExtension}`; // Append timestamp to the original file name
    const destinationPath = path.join(uploadFolder, newFileName);

    // Copy the CSV file to the upload folder with the new name
    fs.copyFile(filePath, destinationPath, (err) => {
        if (err) {
            mainWindow.webContents.send('upload-status', 'Error uploading CSV.');
            console.error(err);
        } else {
            mainWindow.webContents.send('upload-status', `CSV uploaded successfully as ${newFileName}.`);

        }
    });
});

// Handle query submission by calling the helper function
ipcMain.on('run-python-query', (event, query) => {
        inviokeScript('query.py', {"query":query}, event);
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
