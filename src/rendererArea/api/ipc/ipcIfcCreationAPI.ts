export interface IElectronIPCSystemAPI {
    receiveConvertProgress: (callback) => void;
}

declare global {
    interface Window {
        electronIfcCreationAPI: IElectronIPCSystemAPI;
    }
}
