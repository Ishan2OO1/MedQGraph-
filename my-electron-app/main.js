const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

let mainWindow;

app.whenReady().then(() => {
    mainWindow = new BrowserWindow({
        width: 1000,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false, // Required for IPC communication
        }
    });

    mainWindow.loadFile('navigate.html'); // Load your main UI file
});

// ✅ Function to Invoke a Python Script
function invokeScript(scriptName, params, event) {
    const scriptPath = path.join(__dirname, 'helper', scriptName);
    const command = `python "${scriptPath}" '${JSON.stringify(params)}'`;

    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error.message}`);
            event.sender.send('query-script-status', 'Error executing Python script.');
            return;
        }
        if (stderr) {
            console.error(`Python script error: ${stderr}`);
            event.sender.send('query-script-status', 'Python script encountered an error.');
            return;
        }

        console.log(`Python script output: ${stdout}`);
        event.sender.send('query-script-status', stdout);
    });
}

// ✅ Function to Invoke `creatingGraph.py`
function invokeCreatingGraphScript(filePath, event) {
    const pythonScriptPath = path.join(__dirname, 'helper', 'creatingGraph.py');

    exec(`python "${pythonScriptPath}" "${filePath}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error.message}`);
            event.sender.send('python-script-status', 'Error executing Python script.');
            return;
        }
        if (stderr) {
            console.error(`Python script error: ${stderr}`);
            event.sender.send('python-script-status', 'Python script encountered an error.');
            return;
        }
    
        try {
            console.log(`Raw Python output:`, stdout.trim());

            const jsonOutput = stdout.trim();
            if (jsonOutput.startsWith("{") && jsonOutput.endsWith("}")) {
                const output = JSON.parse(jsonOutput);
                const graphPath = output.graph_path;

                event.sender.send('display-graph', graphPath);
            } else {
                console.error("Python script output is not valid JSON:", jsonOutput);
                event.sender.send('python-script-status', 'Invalid JSON output from Python script.');
            }
        } catch (e) {
            console.error("Error parsing Python output:", e);
            event.sender.send('python-script-status', 'Failed to parse Python output.');
        }
    });
}

// ✅ Handle CSV Upload
ipcMain.on('process-csv', (event, filePath) => {
    const uploadFolder = path.join(__dirname, 'uploads');

    if (!fs.existsSync(uploadFolder)) {
        console.log('Creating upload folder...');
        fs.mkdirSync(uploadFolder, { recursive: true });
    }

    const fileExtension = path.extname(filePath);
    const timestamp = Date.now();
    const originalFileName = path.basename(filePath, fileExtension);
    const newFileName = `${originalFileName}-${timestamp}${fileExtension}`;
    const destinationPath = path.join(uploadFolder, newFileName);

    console.log(`Saving CSV to: ${destinationPath}`);

    fs.copyFile(filePath, destinationPath, (err) => {
        if (err) {
            console.error('Error uploading CSV:', err);
            event.sender.send('upload-status', 'Error uploading CSV.');
        } else {
            console.log(`CSV uploaded successfully as ${newFileName}`);
            event.sender.send('upload-status', `CSV uploaded successfully as ${newFileName}`);

            invokeCreatingGraphScript(destinationPath, event);
        }
    });
});

// ✅ Listen for Requests to Open Graph
ipcMain.on('load-graph', (event, graphPath) => {
    mainWindow.loadURL(`file://${graphPath}`);
});

// ✅ Open file dialog to select CSV file
ipcMain.on('open-file-dialog', async (event) => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openFile'],
        filters: [{ name: 'CSV Files', extensions: ['csv'] }]
    });

    if (result.canceled) {
        event.sender.send('upload-status', 'File selection was canceled.');
    } else {
        const filePath = result.filePaths[0];
        event.sender.send('upload-status', 'CSV file selected.');
        ipcMain.emit('process-csv', event, filePath);
    }
});

// ✅ Handle Python Query Execution
ipcMain.on('run-python-query', (event, query) => {
    invokeScript('query.py', { "query": query }, event);
});

// ✅ Handle navigation
ipcMain.on('navigate-to-upload', () => {
    mainWindow.loadFile('uploadcsv.html');
});

ipcMain.on('navigate-to-query', () => {
    mainWindow.loadFile('query.html');
});

ipcMain.on('navigate-to-home', () => {
    mainWindow.loadFile('navigate.html');
});

// ✅ Quit app when all windows are closed
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
