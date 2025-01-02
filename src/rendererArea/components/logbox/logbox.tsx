import React, { useState } from "react"
import { useConverterPageStore } from "../../pages/converter/converterPageStore";


export const LogBox:React.FC = () => {
    const {
        logs
    } = useConverterPageStore();

    return (
        <textarea className="w-full h-full border resize-none" value={logs.join("\n")} readOnly={true}>
        </textarea>
    )
}