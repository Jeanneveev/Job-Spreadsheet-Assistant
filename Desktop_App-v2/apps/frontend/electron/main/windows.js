/* Holds the logic for the different windows */

const { BrowserWindow } = require("electron");
const path = require("path");
const srcDirectory = path.join(__dirname, "..", "..", "src");

const createHomeWindow = () => {
    win = new BrowserWindow({
        width: 400,
        height: 300,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: true,
            preload: path.resolve(__dirname, "preload.js")
        }
    });
    win.loadFile(path.join(srcDirectory, "index.html"));

    return win;
}

const createWindow = (name, width, height, htmlFile) => {
    return new BrowserWindow({
        width: 400,
        height: 300,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: true,
            preload: path.resolve(__dirname, "preload.js")
        }
    })
    .once("ready-to-show", () => { this.show(); })
    .loadFile(path.join(srcDirectory, "pages", `${name}`, `${htmlFile}`));
}

module.exports = { createWindow, createHomeWindow }