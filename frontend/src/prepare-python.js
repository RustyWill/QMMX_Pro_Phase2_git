const { spawn } = require('child_process');
const path = require('path');
const isDev = require('electron-is-dev');

function startPythonBackend() {
  const pythonScript = isDev
    ? path.join(__dirname, '..', '..', 'backend', 'app.py')
    : path.join(process.resourcesPath, 'app', 'backend', 'app.py');

  const pythonProcess = spawn('python', [pythonScript]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`[PYTHON] ${data.toString()}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`[PYTHON ERROR] ${data.toString()}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`[PYTHON] Process exited with code ${code}`);
  });
}

module.exports = { startPythonBackend };
