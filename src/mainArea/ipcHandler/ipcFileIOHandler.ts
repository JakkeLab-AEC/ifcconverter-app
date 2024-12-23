import { dialog, IpcMain } from "electron";
import { AppController } from "../appController/appController";
import { loadJSONWithDialog } from "../appController/utils/fileIOUtils"

export function setIPCFileIOHandler(ipcMain: IpcMain) {
    ipcMain.handle("set-ifc-path", async (_) => {
        const setPathDialog = await dialog.showSaveDialog({
            title: "IFC 파일 저장",
            defaultPath: "output.ifc",
            filters: [
                { name: "IFC file", extensions: ["ifc"] },
            ],
        });

        if(setPathDialog.canceled) {
            return {result: false, message: "No file path selected"};
        } else {
            AppController.getInstance().getDataStore().setIfcPath(setPathDialog.filePath);
            return {result: true, path: setPathDialog.filePath};
        }
    });

    ipcMain.handle("load-mapping-table", async (_) => {
        loadJSONWithDialog();
        return {result: true}
    });
}