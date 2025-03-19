const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const { exec } = require("child_process");
const fetch=require("node-fetch");
const path=require("path");
const { electron } = require('process');

/**
 * Connects to the Flask app, then creates the window
 */
let flaskProc=null;
const connectToFlask=function(){
    //test version
    const venvPath="./py/.venv/bin/python3"
    const scriptPath='./py/routes.py'
    flaskProc = require('child_process').spawn("wsl", [venvPath, "-u", scriptPath]);
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
    });
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
let win=null;
const createWindow = () => {
    win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences:{
            nodeIntegration: true,
            contextIsolation: true,
            preload: path.resolve(app.getAppPath(), 'preload.js')
        }
    });
    win.setAlwaysOnTop("true",'screen-saver', 1);

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
 * Print a message to the VSCode Terminal, only for development
 */
ipcMain.on("print-to-main-terminal",(event,message)=>{
    console.log(message);
})

/**
 * Create a popup browser window, listen for the auth landing page,
 * and send the code back when/if it is reached.
 */
let authWindow=null;
ipcMain.on("open-auth-window", (event,authURL)=>{
    authWindow=new BrowserWindow({
        width: 400,
        height: 500,
        webPreferences: {
            nodeIntegration: false, //for security
        },
    });
    authWindow.setAlwaysOnTop("true",'pop-up-menu', 1)
    authWindow.loadURL(authURL);

    /* If the landing page is reached, pass the code and close the popup */
    authWindow.webContents.on("did-navigate", (ev,url)=>{
        // console.log("URL is:", url);
        if(url.includes("/auth_landing_page/?")){
            const urlParams=new URLSearchParams(new URL(url).search);
            const codeParam=urlParams.get("code");

            if(codeParam!=null){
                console.log("Code is:", codeParam);
                event.sender.send("auth-code-recieved",codeParam);
                authWindow.close();
                authWindow=null;
            }
        }
    });

    authWindow.on("closed",()=>{
        authWindow=null;
    });
});

/**
 * Create a confirmation message box
 *  This is done because just using confirm() in the renderer proc causes a bug with text inputs
  */
ipcMain.on("open-confirm-box", (event,message)=>{
    dialog.showMessageBox(win, {
        "type": "question",
        "title": "Confirmation",
        "message": message,
        "buttons": ["Yes", "No"]
    })
    .then((result)=>{
        if(result.response===0){
            event.sender.send("confirm-box-confirmed");
        }else{
            event.sender.send("confirm-box-denied");
            return;
        }
    })
});
ipcMain.on("open-alert", (event,message)=>{
    dialog.showMessageBox(win, {
        "type": "warning",
        "title": "Warning",
        "message": message,
        "buttons": ["OK"]
    })
    .then((result)=>{
        console.log("Alert closed");
        return;
    })
});


let choiceWindow=null;
ipcMain.on("open-choices-window",(event)=>{
    choiceWindow=new BrowserWindow({
        width: 400,
        height: 500,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.resolve(app.getAppPath(), 'preload.js'),   //add preload to be able to use ipcRenderer in popup
            sandbox: false  //to allow path to be imported in the preload script
        },
    });
    choiceWindow.setAlwaysOnTop("true",'pop-up-menu', 1)
    choiceWindow.loadFile('addChoices.html');

    choiceWindow.on("closed",()=>{
        choiceWindow=null;
    });
});
ipcMain.on("close-choices",(event)=>{
    if(choiceWindow){
        choiceWindow.close();
    }
})