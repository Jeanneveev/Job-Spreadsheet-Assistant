const { app, BrowserWindow, ipcMain } = require('electron');
const { exec } = require("child_process");
const fetch=require("node-fetch");
const path=require("path");

/**
 * Connects to the Flask app, then creates the window
 */
let flaskProc=null;
const connectToFlask=function(){
    //test version
    const venvPath="./py/.venv/bin/python3"
    const scriptPath='./py/routes.py'
    flaskProc = require('child_process').spawn("wsl", [venvPath,scriptPath]);
    //executable version
    //flaskProc = require('child_process').execFile("routes.exe");
    /* For some reason, this part runs during shutdown too */
    flaskProc.stdout.on('data', function (data) {  
        const output = data.toString('utf8');
        console.log("FLASK RUNNING! data:", output);
        /* Wait until Flask server is running to create the window */
        if(output.includes("Flask server running")){
            createWindow();
        }
    });
    // if can't connect
    flaskProc.on('error', (err) => {
        console.error('Failed to start Flask process:', err);
        flaskProc = null;
    });
    // when Flask errors
    //  also prints request info for some reason
    flaskProc.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
        // console.log(`stderr: ${data}`);
    });
    // //logging data
    // flaskProc.stdout.on('data', (data) => {
    //     console.log(`stdout: ${data}`);
    // });
    // on Flask close
    flaskProc.on("close", (code)=>{
        console.log(`child process exited with code ${code}`);
        flaskProc=null;
    });
}

/**
 * Setting up quitting flag for on close event
 */
isAppQuitting=false;
app.on("before-quit",(evt)=>{
    isAppQuitting=true;
});

/**
 * Create a new BrowserWindow that's connected to Flask with index.html as its UI
 */
const createWindow = () => {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences:{
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    win.loadFile('index.html');
    win.on('close', (evt) => {
        if(!isAppQuitting){
            evt.preventDefault();   //pause shutdown to run one last request
            if (flaskProc) {
                console.log("Attempting graceful exit of Flask...")
                fetch("http://127.0.0.1:5000/shutdown",{method:"POST"})
                .then((response) => {
                    /* If the response doesn't come back, Flask has probably already shut down itself
                        This should cause some sort of ECONN error first, but handling it jic
                    */
                    if (!response.ok) {
                        console.error("Flask shutdown request failed:", response.status);
                        flaskProc.kill('SIGINT');   //kill Flask jic
                        flaskProc=null;
                        return;
                    }
                    /* Otherwise, Flask was shutdown */
                    console.log("Flask shutdown request successful.");
                    flaskProc=null;
                })
                .catch((error) => {
                    console.error("Error with shutdown request:", error);
                    flaskProc.kill('SIGINT');
                    flaskProc = null;
                });
            }
            //close again, properly this time
            isAppQuitting=true; //reset flag to skip if block
            win.close();
        }
    });
}

/**
 * When all the windows close, quit the app
 */
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin'){
        app.quit();
    }
});
/**
 * When Electron is closed through the terminal, also kill Flask
 */
app.on('quit', () => {
    if (flaskProc) {
        console.log("Quitting: Sending SIGINT to Flask process...");
        flaskProc.kill('SIGINT');
    }
});

/**
 * Wait for the app to be ready, then create a new window
 */
app.whenReady().then(() => {
    connectToFlask();
    // createWindow();
});

/**
 * Listen for the redirect from the Google log-in popup
 */
ipcMain.on('auth-url-opened', (event) => {
    console.log("Recieved redirect");
});