const { app, BrowserWindow, ipcMain, dialog, remote } = require('electron');
const { exec } = require("child_process");
const fetch=require("node-fetch");
const path=require("path");
const { electron } = require('process');
//Paths
const rootDirectory = path.resolve(__dirname, "..", "..", "..");
console.log("Root directory is", rootDirectory)
const appsDirectory = path.join(rootDirectory, "apps");
const pagesDirectory = path.join(appsDirectory, "frontend", "pages");
const backendDirectory = path.resolve(rootDirectory, "..", "..", "backend");
//Other
const SERVER_URL = "http://127.0.0.1:5000";

/**
 * Connects to the Flask app, then creates the window
 */
let flaskProc=null;
const createFlaskProc = () => {
    //dev
    const scriptPath = "backend.routes.run"
    let activateVenv;
    let command;
    let args;
    if (process.platform == "win32") {
        activateVenv = path.join(rootDirectory, ".venv", "Scripts", "activate");
        command = "cmd";
        args = ["/c", `${activateVenv} && python -m ${scriptPath}`]
    } else {    //Mac or Linux
        activateVenv = path.join(rootDirectory, ".venv", "bin", "python");
        //Mac and Linux should be able to directly spawn it
        command = activateVenv;
        args = ["-m", scriptPath];
    }

    //run the venv and start the script
    //NOTE: this goes off the apps/ folder, acting as if that is the root directory
    return require("child_process").spawn(command, args, {
        cwd: appsDirectory,
        env: {
            ...process.env,
            PYTHONPATH: appsDirectory,
            PYTHONUNBUFFERED: '1'  // have Python not buffer stdout
        },
        shell: true  // required for "&&" to work on Windows
    });
}

const waitForFlaskRunning = (flaskProc=null, timeoutMS) => {
    /* Returns a Promise that resolves if Flask prints out the trigger term
        within a certain span of time and rejects if it cannot
    */
    return new Promise((resolve, reject) => {
        if(!flaskProc){
            reject(new Error("Flask process is null. There is nothing to wait for"));
            return;
        }

        //making output listener its own functions so it can be removed later
        //  w/o messing up the one in connectToFlask()
        const dataListener = (data) =>{
            const output = data.toString('utf8');
            console.log("FLASK RUNNING!");
            /* Wait until Flask server is running to create the window */
            if(output.includes("Serving Flask")){
                clearTimeout(timer);
                flaskProc.stdout.off("data", dataListener); //remove listener
                setTimeout(resolve, 500); //wait a bit to complete startup
            }
        }

        let timer = setTimeout(() => {
            flaskProc.stdout.off("data", dataListener); //remove listener
            reject(new Error("Flask server did not start within ",timeoutMS," ms"));
        }, timeoutMS);

        flaskProc.stdout.on('data', dataListener);
    });
}

const checkFlaskConnection = () => {
    /* Returns a Promise that resolves if the index page can be fetched
        and rejects if it cannot
    */
    return new Promise((resolve, reject) => {
        if(!flaskProc) {
            reject(new Error("Flask process is null. There is nothing to connect to"));
            return;
        }

        console.log("Attempting connection to Flask...");
        return fetch(`${SERVER_URL}/`,{ method: "GET" })
        .then((response) =>{
            if (!response.ok) { //didn't actually connect to Flask
                console.error("Flask connection request failed:", response.status);
                reject(new Error("Flask connection request failed:", response.status));
                return;
            }
            console.log("Flask connection request successful.");
            return response.text();
        })
        .then((data) => {
            console.log("Flask index endpoint called:", data);
            resolve();
        })
        .catch((error) => {
            // console.error("Error with shutdown request:", error);
            reject(error);
        });
    });
}

const connectToFlask=function(){
    flaskProc = createFlaskProc();
    //executable version
    //flaskProc = require('child_process').execFile("routes.exe");

    /* Wait until Flask server is running to create the window */
    console.log("Waiting for Flask to start...");
    const timeout = 10000;
    waitForFlaskRunning(flaskProc, timeout)
    .then(() => { return checkFlaskConnection(); })
    .then(() => { createWindow(); })
    .catch((err) => {
        console.error(err);
        console.error("Connection unsuccessful");
        //emit an error for the error listener below to catch
        flaskProc.emit("error", err);
    });

    flaskProc.stdout.on('data', (data) => {  
        const output = data.toString('utf8');
        console.log("data:", output);
    });
    flaskProc.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });
    // if can't connect
    flaskProc.on('error', (err) => {
        console.error('Failed to start Flask process:', err);
        flaskProc = null;
        app.quit();
    });
    // when sys.exit(0) is called at the end of Flask shutdown
    flaskProc.on("exit", (code, signal) => {
        console.log(`Python child process exited with code ${code} and signal ${signal}`);
        flaskProc = null;
        if(win){
            win.close();
        }
    });
}

const shutdownFlaskConnection = () => {
    /* Return a promise that resolves if Flask is shutdown/has already shut down
        and rejects if an error other than ECONNRESET occurs
    */
    return new Promise((resolve, reject) => {
        if (!flaskProc) {
            //flaskProc is already null and, assumedly, shut down
            resolve();
            return;
        }

        fetch(`${SERVER_URL}/shutdown`, { method:"POST" })
        .then((response) => {
            if (!response.ok) {
                console.error("Flask shutdown request failed:", response.status);
                reject(new Error("Flask shutdown request failed:", response.status));
                return;
            }
            /* Otherwise, Flask was shutdown */
            console.log("Flask shutdown request successful.");
            return response.text();
        })
        .then((data) => {
            console.log("Flask shutdown endpoint called:", data);
            resolve();
        })
        .catch((error) => {
            /* If the error is ECONNRESET, the Flask app probably already shut down*/
            if(error.code === "ECONNRESET") {
                console.log("Flask connection reset, assuming shutdown was successful");
                resolve();
            }else{
                console.error("Error with shutdown request:", error);
                reject(error);  //this already has an error to reject, no need to make a new one
            }
        });
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
        width: 400,
        height: 300,
        webPreferences:{
            nodeIntegration: true,
            contextIsolation: true,
            preload: path.resolve(app.getAppPath(), 'preload.js')
        }
    });
    win.setAlwaysOnTop("true","main-menu", 1);

    win.loadFile(path.join(pagesDirectory, "index.html"));

    win.on('close', (evt) => {
        if(!isAppQuitting){
            evt.preventDefault();   //pause shutdown to run one last request
            console.log("Attempting graceful exit of Flask...");
            //shutdown the Flask app
            shutdownFlaskConnection().then(() => {
                console.log("Shutdown successful. Waiting for Flask process exit");
                isAppQuitting = true;
                // flaskProc.emit("exit", 0, null);
                return;
            }).catch((err) => {
                console.error(err);
                console.error("Shutdown unsuccessful, force quitting Electron");
                isAppQuitting=true; //reset flag
                win.close();    //force close since the Flask event handler won't trigger
            });
        }else{
            console.log("flask is",flaskProc!==null);   //check that flaskProc is null
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
});

/**
 * Print a message to the VSCode Terminal, only for development
 */
ipcMain.on("print-to-main-terminal",(event,message)=>{
    console.log(message);
});

/**
 * Create a second browser window for handling question creation
 */
let questionWindow=null;
ipcMain.on("open-question-window",(event)=>{
    console.log("Question window opening");
    questionWindow=new BrowserWindow({
        width: 600,
        height: 400,
        webPreferences:{
            nodeIntegration: true,
            contextIsolation: true,
            preload: path.resolve(app.getAppPath(), 'preload.js')
        },
        parent: win,
        // modal: true
    });

    win.setAlwaysOnTop("false"); //remove parent's always on top
    questionWindow.setAlwaysOnTop("true","torn-off-menu", 1);

    questionWindow.loadFile(path.join(pagesDirectory, 'selectQuestionGroup.html'));

    questionWindow.on("closed",()=>{
        win.loadFile(path.join(pagesDirectory, "index.html")); //reload main page to activate buttons
        questionWindow=null;
    });
});
ipcMain.on("close-question-window",()=>{
    if(questionWindow){
        questionWindow.close();
        questionWindow=null;
        //reset parent's always on top
        if(win){
            win.setAlwaysOnTop("true","main-menu", 1);
        }
    }
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
                //TODO: Comment out
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
ipcMain.on("open-confirm", (event,message)=>{
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
let promptWindow=null
ipcMain.on("open-prompt", (event)=>{
    promptWindow=new BrowserWindow({
        width: 300,
        height: 175,
        parent: BrowserWindow.getFocusedWindow(),
        autoHideMenuBar: true,
        webPreferences:{
            nodeIntegration: true,
            contextIsolation: true,
            preload: path.resolve(app.getAppPath(), 'preload.js')
        },
    });
    
    questionWindow.setAlwaysOnTop("false"); //remove parent's always on top
    promptWindow.setAlwaysOnTop("true",'pop-up-menu', 1);
    promptWindow.loadFile(path.join(pagesDirectory, "requestSaveName.html"));

    promptWindow.on("closed",()=>{
        promptWindow=null;
    });
});
ipcMain.on("close-prompt",(event)=>{
    if(promptWindow){
        promptWindow.close();
        promptWindow=null;
        //reset parent's always on top
        if(questionWindow){
            questionWindow.setAlwaysOnTop("true","torn-off-menu", 1);
        }
    }
})

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
    choiceWindow.loadFile(path.join(pagesDirectory, 'addChoices.html'));

    choiceWindow.on("closed",()=>{
        choiceWindow=null;
    });
});
ipcMain.on("close-choices",(event)=>{
    if(choiceWindow){
        choiceWindow.close();
        choiceWindow=null;
    }
})