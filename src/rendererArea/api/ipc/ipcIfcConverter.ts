export interface IfcConverter {
    sendMessageToIfcConverter: (message: string) => Promise<void>;
    mappingTest: () => void;
}

declare global {
    interface Window {
        electronIPCIfcConverter: IfcConverter
    }
}