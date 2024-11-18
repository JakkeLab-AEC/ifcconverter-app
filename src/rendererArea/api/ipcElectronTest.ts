export interface IPCElectronTest {
    sendMessage: () => Promise<string>;
    sendMessageToPython: (message: string) => Promise<void>;
}

declare global {
    interface Window {
        electronIPCElectronTest: IPCElectronTest
    }
}