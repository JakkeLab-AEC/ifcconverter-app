import { dialog, IpcMain } from "electron";
import { AppController } from "../appController/appController";
import { loadJSONWithDialog, loadTargetFileWithDialog, setIfcFileWithDialog } from "../appController/utils/fileIOUtils"

export function setIPCFileIOHandler(ipcMain: IpcMain) {
    ipcMain.handle("set-ifc-path", async (_) => {
        const jobResult = setIfcFileWithDialog();
        return jobResult;
    });

    ipcMain.handle("load-mapping-table", async (_) => {
        const jobResult = loadJSONWithDialog();
        return jobResult;
    });

    ipcMain.handle("set-target-file", async(_) => {
        const jobResult = loadTargetFileWithDialog();
        return jobResult
    });
}