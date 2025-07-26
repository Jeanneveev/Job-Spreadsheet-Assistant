/* Holds the logic for the different windows */

const { BrowserWindow } = require("electron");
const path = require("path");
const srcDirectory = path.join(__dirname, "..", "..", "src");
const preloadDirectory = path.resolve(__dirname, "..", "preload", "preload.js")

const createHomeWindow = () => {
    win = new BrowserWindow({
        width: 400,
        height: 300,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: true,
            preload: preloadDirectory
        }
    });
    win.loadFile(path.join(srcDirectory, "index.html"));

    return win;
}

const createWindow = (width, height, foldername, filename, parent=null) => {
    if(parent == null){
        window = new BrowserWindow({
            width: width,
            height: height,
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: true,
                preload: preloadDirectory
            }
        });
    }else{
        window = new BrowserWindow({
            width: width,
            height: height,
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: true,
                preload: preloadDirectory
            },
            parent: parent
        });
    }
    window.loadFile(path.join(srcDirectory, "pages", foldername, filename));

    return window;
}

module.exports = { createWindow, createHomeWindow }