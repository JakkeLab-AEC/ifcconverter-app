import { BrowserWindow, IpcMain } from "electron";
import path from "path";
import { UIController } from "../appController/controllers/uicontroller";

export const setIpcWindowControl = (ipcMain: IpcMain) => {
    ipcMain.handle('window-control-minimize', (_) => {
        const mainWindow = UIController.instance.getWindow('main-window');
        if (mainWindow) {
            mainWindow.minimize();
        } else {
            console.error('Main window is undefined');
        }
    });

    // ipcMain.handle('window-control-maximize', (_) => {
    //     const mainWindow = UIController.instance.getWindow('main-window');
    //     if (mainWindow) {
    //         if (mainWindow.isMaximized()) {
    //             mainWindow.unmaximize();
    //         } else {
    //             mainWindow.maximize();
    //         }
    //     } else {
    //         console.error('Main window is undefined');
    //     }
    // });

    ipcMain.handle('window-control-quit', (_) => {
        const mainWindow = UIController.instance.getWindow('main-window');
        if (mainWindow) {
            mainWindow.close();
        } else {
            console.error('Main window is undefined');
        }
        UIController.instance.removeWindow('main-window');
    });
}