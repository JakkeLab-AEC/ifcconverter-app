import React from "react"

type Log ={
    logId: string,
    log: string,
    time: Date,
}

export const LogBox:React.FC = () => {
    const [logs, setLogs] = React.useState<Log[]>([]);
    return (
        <div className="flex flex-col gap-2">
            <div>
                실행 로그
            </div>
            <textarea className="w-full h-48 border resize-none" value={logs.map((log) => `${log.time.toISOString()} ${log.log}`).join('\n')} readOnly={true}>
            </textarea>
        </div>
    )
}