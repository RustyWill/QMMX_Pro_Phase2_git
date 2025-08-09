const path = require('path');
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess = null;

function startPythonBackend() {
  const scriptPath = path.join(__dirname, '..', 'backend', 'app.py');

  pythonProcess = spawn('python', [scriptPath]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`[PYTHON] ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`[PYTHON ERROR] ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`[PYTHON] Backend exited with code ${code}`);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    icon: path.join(__dirname, '..', 'qmmx-icon.ico'),
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // ✅ Correct path for production mode (after build)
  mainWindow.loadFile(path.join(__dirname, 'build', 'index.html'));

  // Uncomment if you want to open dev tools automatically
  // mainWindow.webContents.openDevTools();

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  startPythonBackend();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
