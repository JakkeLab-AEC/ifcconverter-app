import React, { useEffect, useRef, useState } from "react"
import { Header } from './components/window/header';
import { appInfo } from "../appConfig";
import { LogBox } from "./components/logbox/logbox";
import { SetIFCPath } from "./components/packagedComponents/setIfcPath";
import { LoadedMappingTable } from "./components/packagedComponents/loadedMappingTable";
import { ProgressBar } from "./components/progressbar/progressbar";

export const HomeScreen:React.FC = () => {
    const ifcFilePathRef = useRef<HTMLInputElement>(null);
    const ipcPythonTest = async () => {
        const message = "Test From Electron";
        await window.electronIPCIfcConverter.sendMessageToIfcConverter(message);
    }

    return (
        <div className="flex flex-col">
            <div style={{width:'100%'}}>
                <Header appName={appInfo.ApplicationName} />
            </div>
            <div className="flex flex-col p-4 gap-2">
                <SetIFCPath />
                <hr/>
                <LoadedMappingTable />
                <hr/>
                <div>
                    <LogBox />
                </div>
                <div>
                    <ProgressBar value={50} />
                </div>
                <div>
                    <button className="border" onClick={ipcPythonTest}>IPC Python Test</button>
                </div>
            </div>
        </div>
    )
}
