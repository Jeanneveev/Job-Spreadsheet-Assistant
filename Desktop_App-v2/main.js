const { app, BrowserWindow } = require('electron');
const { exec } = require("child_process");
const fetch=require("node-fetch");

/**
 * Connects to the Flask app
 */
let flaskProc=null;
const connectToFlask=function(){
    //test version
    flaskProc = require('child_process').spawn('py', ['./py/routes.py']);
    //executable version
    //flaskProc = require('child_process').execFile("routes.exe");
    flaskProc.stdout.on('data', function (data) {  
        console.log("FLASK RUNNING! data:", data.toString('utf8'));  
    });
    // if can't connect
    flaskProc.on('error', (err) => {
        console.error('Failed to start Flask process:', err);
        flaskProc = null;
    });
    // when Flask errors
    flaskProc.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
        console.log(`stderr: ${data}`);
    });
    // on Flask close
    flaskProc.on("close", (code)=>{
        console.log(`child process exited with code ${code}`);
        flaskProc=null;
    });
}

/**
 * Create a new BrowserWindow that's connected to Flask with index.html as its UI
 */
isAppQuitting=false;
app.on("before-quit",(evt)=>{
    isAppQuitting=true;
});

const createWindow = () => {
    const win = new BrowserWindow({
        width: 800,
        height: 600
    });

    connectToFlask();

    win.loadFile('index.html');
    // On window close (when the Electron app is exited), gracefully shut down Flask
    // win.on('closed', () => {
    //     if (flaskProc) {
    //         console.log("Closing: Sending SIGINT to Flask process...");
    //         flaskProc.kill('SIGINT'); // Send SIGINT (Ctrl+C) to Flask
    //         flaskProc=null; //setting flaskProc to null to prevent quit event from killing it twice
    //     }
    // });
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
                    /* Otherwise, return the return and continue the chain */
                    return response.text();
                })
                .then((data) => {
                    console.log("Flask shutdown request successful.");
                    console.log(data);
                    flaskProc.kill('SIGINT');   //kill Flask
                    flaskProc=null;
                })
                .catch((error) => {
                    console.error("Error with shutdown request:", error);
                    flaskProc.kill('SIGINT'); // Kill even if there is an issue with the request
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
    createWindow();
});