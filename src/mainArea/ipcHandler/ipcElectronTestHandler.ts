import { IpcMain } from "electron";
import { AppController } from "../../mainArea/appController";

export function setIPCElectronTestHandler(ipcMain: IpcMain) {
    ipcMain.handle('electron-test', async () => {
        const randomWords = [
            "apple",
            "mountain",
            "ocean",
            "river",
            "forest",
            "sky",
            "breeze",
            "cloud",
            "sunlight",
            "flower"
        ];

        const index = Math.trunc(Math.random()*10);

        return randomWords[index];
    })

    ipcMain.handle('electron-python-test', async (_, message: string) => {
        const handler = AppController.getInstance().getPythonProcessHandler();
        handler.start();

        (async () => {
            try {
                const response = await handler.sendMessage({
                    action: 'greet',
                    name: 'John Doe',
                });
                console.log(`------Python Response------`);
                console.log(response);
                console.log(`---------------------------`);
            } catch(error) {
                console.log(error);
            } finally {
                handler.stop();
            }
        })();
    });
}