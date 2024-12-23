export interface IfcConverter {
    sendMessageToIfcConverter: (message: string) => Promise<void>;
}

declare global {
    interface Window {
        electronIPCIfcConverter: IfcConverter
    }
}