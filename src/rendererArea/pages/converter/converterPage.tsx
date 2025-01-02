import React from "react"
import { SetPath } from "../../components/packagedComponents/setPath"
import { LogBox } from "../../components/logbox/logbox"
import { ProgressBar } from "../../components/progressbar/progressbar"
import { useConverterPageStore } from "./converterPageStore"
import { getCurrentTimestamp } from "../../../commonUtils/timeStamper"

export const ConverterPage:React.FC = () => {
    const {
        pathMappingTable,
        pathTargetFile,
        pathIfcFile,
        currentProgress,
        logs,
        setMappingTable,
        setTargetFile,
        setIfcFile,
        pushLog,
        flushLogs,
    } = useConverterPageStore();

    const runConvert = async () => {
        flushLogs();
        const message = "Run Convert";
        pushLog(`[${getCurrentTimestamp()}] Initialize.`)
        await window.electronIPCIfcConverter.sendMessageToIfcConverter(message);
    }

    const ipcMappingTest = () => {
        window.electronIPCIfcConverter.mappingTest();
    }

    return (
        <div className="flex flex-col p-4 gap-2 h-full">
            <div className="font-bold" style={{fontSize: 20}}>
                설정
            </div>
            <SetPath label="매핑 테이블" path={pathMappingTable} onClickLoadPath={setMappingTable}/>
            <hr/>
            <SetPath label="변환할 파일" path={pathTargetFile} onClickLoadPath={setTargetFile}/>
            <hr/>
            <div className="font-bold" style={{fontSize: 20}}>
                저장 설정
            </div>
            <SetPath label="저장 경로" path={pathIfcFile} onClickLoadPath={setIfcFile}/>
            <hr />
            <div className="flex">
                <button className="border w-full rounded-md" onClick={runConvert}>변환하기</button>
            </div>
            {/* <div className="flex">
                <button className="border w-full rounded-md" onClick={ipcMappingTest}>매핑테스트</button>
            </div> */}
            <div className="flex flex-grow h-[360px]">
                <LogBox />
            </div>
            <div>
                <ProgressBar value={currentProgress} />
            </div>
        </div>
    )
}