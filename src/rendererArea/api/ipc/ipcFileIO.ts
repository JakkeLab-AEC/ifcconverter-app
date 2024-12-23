export interface IElectronFileIOAPI {
    setIfcPath:() => Promise<{result: boolean, path?: string, message?: string}>
    loadMappingTable: () => Promise<{result: boolean, message?: string}>
}

declare global {
    interface Window {
        electronFileIOAPI: IElectronFileIOAPI;
    }
}