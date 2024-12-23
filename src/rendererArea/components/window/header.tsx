import React, { useState } from "react"
import ServiceLogo from "./details/servicelogo"
import { useHomeStore } from "../../homeStore";
import { ContextMenu, ContextMenuProp } from "../contextmenu/contextMenu";
import './headerStyle.css';

export const Header: React.FC<{appName: string}> = ({appName}) => {
    const [menuVisibility, setMenuVisibility] = useState<boolean>(false);
    const {
        osName
    } = useHomeStore();

    const contextMenuProp:ContextMenuProp = {
        menuItemProps: [{
            displayString: '매핑 테이블 불러오기',
            isActionIdBased: false,
            action: async () => { await window.electronFileIOAPI.loadMappingTable() },
            closeHandler: () => setMenuVisibility(false),
        }],
        width: 180,
        onClose: () => setMenuVisibility(false),
    }

    const onClickMenu = () => {
        if(menuVisibility) {
            setMenuVisibility(false);
        } else {
            setMenuVisibility(true);
        }
    }

    return (
        <div className={`w-full flex key-color-main h-[48px] items-center ${osName == 'win32' ? 'pl-4' : 'pl-20'} pr-4`} style={{borderBottomWidth: 2, borderColor: "black", userSelect: 'none'}}>
            <div className="main-header flex-grow">
                <ServiceLogo appName={appName} />
            </div>
            { menuVisibility && 
            <div style={{position: 'absolute', right: 220, top: 40}}>
                <ContextMenu 
                    menuItemProps = {contextMenuProp.menuItemProps} 
                    width={contextMenuProp.width} 
                    onClose={contextMenuProp.onClose} />
            </div>}
            {osName == 'win32' && 
            <div className="flex flex-row gap-4">
            <button onClick={() => onClickMenu()} className="menu-btn-neutral-rect">
                메뉴
            </button>
            {/* Minimize Button */}
            <button onClick={() => {window.electronWindowControlAPI.minimize()}} className="menu-btn-neutral">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke='black'>
                    <line x1="3" y1="7" x2="13" y2="7" strokeWidth="1"/>
                </svg>
            </button>

            {/* Maximize/Restore Button */}
            {/* ipcRenderer.send('window-control', 'maximize') */}
            {/* <button onClick={() => {window.electronWindowControlAPI.maximize()}} className="menu-btn-neutral">
                <svg width="16" height="16" viewBox="0 0 16 16"  fill="none" stroke="black">
                    <rect x="3" y="3" width="10" height="10" strokeWidth={1}/>
                </svg>
            </button> */}
            {/* Close Button */}
            {/* ipcRenderer.send('window-control', 'close') */}
            <button onClick={() => {window.electronWindowControlAPI.quit()}} className="menu-btn-negative">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="black">
                    <line x1="3" y1="3" x2="13" y2="13" strokeWidth="1"/>
                    <line x1="3" y1="13" x2="13" y2="3" strokeWidth="1"/>
                </svg>
            </button>
            </div>}
        </div>
    )
}