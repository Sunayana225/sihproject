// This script helps start the Python Flask backend
const { spawn } = require('child_process');
const path = require('path');

function startBackend() {
    const pythonScript = path.join(__dirname, 'app.py');
    
    console.log('Starting Flask backend...');
    
    // Try python first, then python3
    const pythonCommands = ['python', 'python3', 'py'];
    
    for (const pythonCmd of pythonCommands) {
        try {
            const backend = spawn(pythonCmd, [pythonScript], {
                cwd: __dirname,
                stdio: 'inherit'
            });
            
            backend.on('error', (err) => {
                console.error(`Failed to start backend with ${pythonCmd}:`, err.message);
            });
            
            backend.on('close', (code) => {
                console.log(`Backend process exited with code ${code}`);
            });
            
            console.log(`Flask backend started with ${pythonCmd}`);
            return backend;
        } catch (error) {
            console.error(`Failed to start with ${pythonCmd}:`, error.message);
        }
    }
    
    console.error('Could not start Python backend. Please ensure Python is installed.');
}

// Start the backend if this script is run directly
if (require.main === module) {
    startBackend();
}

module.exports = { startBackend };