const { app, BrowserWindow } = require('electron');
const fetch = require('node-fetch');
const path = require("path");
const { spawn } = require("child_process");
const { time } = require('console');
// Paths
const rootDirectory = path.join(__dirname, "..","..","..","..")
const electronDirectory = __dirname;
const pagesDirectory = path.join(electronDirectory, "..", "pages")
const backendDirectory = path.join(rootDirectory, "apps", "backend")
// Other
const SERVER_URL = "http://127.0.0.1:5000";

/**
 * Connects to the Flask app, then creates the window
 */
let flaskProc = null;
const createFlaskProc = () => {
    //dev
    const scriptPath = "apps.backend.flask_app.run"
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
    return require("child_process").spawn(command, args, {
        env: {
            ...process.env,
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

const connectToFlask = () => {
    // NOTE: despite being called flaskProc, it's specifically a Python thread that's running,
    // among some other Python code, a Flask app
    flaskProc = createFlaskProc();

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
 * Create a new BrowserWindow that's connected to Flask with index.html as its UI
 */
let isAppQuitting=false;    //flag for on close event
let win=null;
const createWindow = () => {
    win = new BrowserWindow({
        width: 400,
        height: 300,
        webPreferences:{
            nodeIntegration: true,
            contextIsolation: true,
            preload: path.resolve(app.getAppPath(), "apps", "frontend", "src", "electron", "preload.js")
        }
    });

    win.loadFile(path.join(pagesDirectory, "index.html"));
    /* When the window is closed, the if statement triggers, calls for Flask to shut itself down,
        and changes the flag. Then the flaskProc will exit and trigger on close again.
        The second time, the if statement will fail, allowing the window to close properly.
        That will then trigger window-all-closed and the app will quit.
    */
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
 * Wait for the app to be ready, then create a new window
 */
app.whenReady().then(() => {
    connectToFlask();
});