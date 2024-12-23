import { app, BrowserWindow, ipcMain, Menu, MenuItemConstructorOptions } from 'electron';
import { setIPCElectronIFCHandler } from './mainArea/ipcHandler/ipcIFCConvertHandler';
import path from 'path';
import os from 'os';
import { AppController } from './mainArea/appController/appController';
import { UIController } from './mainArea/appController/controllers/uicontroller';
import { setIpcWindowControl } from './mainArea/ipcHandler/ipcWindowControl';
import { setIPCFileIOHandler } from './mainArea/ipcHandler/ipcFileIOHandler';

if (require('electron-squirrel-startup')) app.quit();

let mainWindow: BrowserWindow | null;

const createWindow = () => {
  console.log(path.join(__dirname, 'preload.js'));
  mainWindow = new BrowserWindow({
    width: 480,
    height: 600,
    title: 'Commonland Desktop',
    titleBarStyle: os.platform() == 'win32'? 'hidden' : 'hiddenInset',
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: true,
      devTools: !app.isPackaged,
    },
  });
  
  if (!app.isPackaged) {
    mainWindow.loadURL('http://localhost:3000');
  } else {
    mainWindow.loadFile(path.join(__dirname, '../.vite/index.html'));
  }

  // Send os info
  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow?.webContents.send('os-info', {
      platform: os.platform(),
      arch: os.arch(),
      release: os.release(),
      mode: app.isPackaged ? 'dist' : 'dev'
    });
  });
  
  mainWindow.on('closed', () => {
    mainWindow = null;
    app.quit();
  });

  // Prevent refresh on dist environment
  if(app.isPackaged) {
    mainWindow.webContents.on('before-input-event', (event, input) => {
      if (
        input.key === 'F5' || 
        (input.control && input.key === 'r') || 
        (input.control && input.shift && input.key === 'R')
      ) {
        event.preventDefault();
      }
    });
  }

  // Menu template
  const submenus: MenuItemConstructorOptions[] = [
    {role: 'about'},
    {role: 'quit'},
  ];

  const menuOption: MenuItemConstructorOptions = {
    label: 'Edit',
    submenu: submenus
  };

  if(!app.isPackaged) {
    submenus.push({role: 'toggleDevTools'});
    submenus.push({role: 'reload'});
  }
  
  const template:MenuItemConstructorOptions[] = [menuOption];
  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
  
  UIController.initiate();
  UIController.instance.registerWindow('main-window', mainWindow);
};

app.on('ready', () => {
  AppController.InitiateAppController();

  createWindow();

  setIPCElectronIFCHandler(ipcMain);

  setIpcWindowControl(ipcMain);

  setIPCFileIOHandler(ipcMain);
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});