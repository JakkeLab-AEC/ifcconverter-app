import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld('electronIPCIfcConverter', {
    sendMessageToIfcConverter: (message: string) => ipcRenderer.invoke('ifc-create', message),
    mappingTest: () => ipcRenderer.invoke('ifc-mapping-test')
});

contextBridge.exposeInMainWorld('electronWindowControlAPI', {
    minimize: () => ipcRenderer.invoke('window-control-minimize'),
    maximize: () => ipcRenderer.invoke('window-control-maximize'),
    quit: () => ipcRenderer.invoke('window-control-quit'),
});

contextBridge.exposeInMainWorld('electronSystemAPI', {
    receiveOSInfo: (callback) => ipcRenderer.on('os-info', (_event, osInfo) => callback(osInfo)),
});

contextBridge.exposeInMainWorld('electronFileIOAPI', {
    setIfcPath: () => ipcRenderer.invoke('set-ifc-path'),
    setMappingTable: () => ipcRenderer.invoke('load-mapping-table'),
    setTargetFilePath: () => ipcRenderer.invoke('set-target-file')
});

contextBridge.exposeInMainWorld('electronIfcCreationAPI', {
    receiveConvertProgress: (callback) => ipcRenderer.on('send-ifc-creation-status', (_event, args) => callback(args)),
});