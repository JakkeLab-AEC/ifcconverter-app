import React, { useState } from "react"

type Log ={
    logId: string,
    log: string,
    time: Date,
}

export const LogBox:React.FC = () => {
    const [logs, setLogs] = useState<Log[]>([]);
    return (
        <textarea className="w-full h-full border resize-none" value={logs.map((log) => `${log.time.toISOString()} ${log.log}`).join('\n')} readOnly={true}>
        </textarea>
    )
}