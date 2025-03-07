process.once("loaded", ()=>{
    const { contextBridge, ipcRenderer } = require('electron')

    contextBridge.exposeInMainWorld("electron",{
        on: (eventName, callback) => ipcRenderer.on(eventName, callback),
        send: (eventName, data) => ipcRenderer.send(eventName,data),
    })
})