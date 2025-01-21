const { app, BrowserWindow } = require('electron')

/**
 * Connects to the Flask app
 */
const connectToFlask=function(){
    let python;
    //test version
    python = require('child_process').spawn('py', ['./py/routes.py']);
    //executable version
    //python = require('child_process').execFile("routes.exe");
    python.stdout.on('data', function (data) {  
        console.log("FLASK RUNNING! data:", data.toString('utf8'));  
    });  
    python.stderr.on('data', (data) => {    // when error
        console.error(`stderr: ${data}`);
        console.log(`stderr: ${data}`);
    });
    python.on("close", (code)=>{
        console.log(`child process exited with code ${code}`);
    });
}

/**
 * Create a new BrowserWindow that's connected to Flask with index.html as its UI
 */
const createWindow = () => {
    const win = new BrowserWindow({
        width: 800,
        height: 600
    });

    connectToFlask();

    win.loadFile('index.html');
}

/**
 * When all the windows close, quit the app
 */
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
});

/**
 * Wait for the app to be ready, then create a new window
 */
app.whenReady().then(() => {
    createWindow();
});