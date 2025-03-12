process.once("loaded", ()=>{
    try {
        console.log('Preload script loaded');
        const { contextBridge, ipcRenderer } = require('electron')
        const path = require('path');

        contextBridge.exposeInMainWorld("electron",{
            on: (eventName, callback) => ipcRenderer.on(eventName, callback),
            send: (eventName, data) => ipcRenderer.send(eventName,data),
            currDir: () => process.cwd(),
            getPath: (filename) => {
                const completePath=path.join(process.cwd(),filename);
                return completePath;
            },
            SERVER_URL: "http://127.0.0.1:5000",
        })
    }catch(error){
        console.error('Error in preload script:', error);
    }
})