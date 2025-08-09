const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow = null;
let backendProcess = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    icon: path.join(__dirname, '../frontend/public/qmmx-icon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  const startUrl = `file://${path.join(__dirname, '../frontend/build/index.html')}`;
  mainWindow.loadURL(startUrl);
}

function startBackend() {
  const backendPath = path.join(__dirname, '../backend/app.py');

  backendProcess = spawn('python', [backendPath], {
    cwd: path.join(__dirname, '../backend'),
    detached: true,
    shell: true,
    stdio: 'ignore',
  });

  backendProcess.unref();
}

app.on('ready', () => {
  startBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
