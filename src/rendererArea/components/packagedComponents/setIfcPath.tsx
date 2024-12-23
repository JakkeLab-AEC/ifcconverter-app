import React, { useRef } from "react";

export const SetIFCPath:React.FC = () => {
    const ifcFilePathRef = useRef<HTMLInputElement>(null);
    
    const onClickSetIFCPath = async () => {
        const jobResult = await window.electronFileIOAPI.setIfcPath();
        
        if(jobResult.result) {
            if (ifcFilePathRef.current && typeof jobResult.path === 'string') {
                ifcFilePathRef.current.value = jobResult.path;
            }
        }
    }
    
    return (
        <div className="flex flex-row gap-2">
            <div className="flex font-bold w-[100px]">
                IFC 저장 경로
            </div>
            <div className="flex flex-grow">
                <input type="text" className="border w-full rounded-md" readOnly={true} ref={ifcFilePathRef}/>
            </div>
            <button className="w-[48px] border rounded-md" onClick={onClickSetIFCPath}>
                설정
            </button>
        </div>
    )
}