import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld('electronIPCElectronTest', {
    sendMessage: () => ipcRenderer.invoke('electron-test'),
    sendMessageToPython: (message: string) => ipcRenderer.invoke('electron-python-test', message),
});