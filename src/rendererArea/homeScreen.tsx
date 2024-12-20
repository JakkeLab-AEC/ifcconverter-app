import React, { useEffect, useState } from "react"

export const HomeScreen = () => {
    const [receivedMessage, setMessage] = useState<string>('');
    const ipcTest = async () => {
        const message = await window.electronIPCElectronTest.sendMessage();
        if(message) {
            setMessage(message);
        }
    }

    const ipcPythonTest = async () => {
        const message = "Test From Electron";
        await window.electronIPCElectronTest.sendMessageToPython(message);
    }

    return (
        <div className="p-2 flex flex-col gap-2">
            <div>
                Call python
            </div>
            <div>
                <button className="border" onClick={ipcPythonTest}>IPC Python Test</button>
            </div>
        </div>
    )
}
