export interface IElectronFileIOAPI {
    setIfcPath:() => Promise<{result: boolean, path?: string, message?: string}>;
    setMappingTable: () => Promise<{result: boolean, path?: string, message?: string, errorCode?: string}>;
    setTargetFilePath: () => Promise<{result: boolean, path?: string, message?: string, errorCode?: string}>;
}

declare global {
    interface Window {
        electronFileIOAPI: IElectronFileIOAPI;
    }
}