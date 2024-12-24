import React, { useEffect, useRef, useState } from "react"
import { Header } from './components/window/header';
import { appInfo } from "../appConfig";;
import { ConverterPage } from "./pages/converter/converterPage"

export const HomeScreen:React.FC = () => {

    return (
        <div className="flex flex-col h-[100%]">
            <Header appName={appInfo.ApplicationName} />
            <ConverterPage />
        </div>
    )
}
