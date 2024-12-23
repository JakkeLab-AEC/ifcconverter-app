import React, { useRef } from "react";

export const LoadedMappingTable:React.FC = () => {
    const ifcFilePathRef = useRef<HTMLInputElement>(null);
    
    return (
        <div className="flex flex-row gap-2">
            <div className="flex font-bold w-[100px]">
                매핑 테이블
            </div>
            <div className="flex flex-grow">
                <input type="text" className="border w-full rounded-md" readOnly={true} ref={ifcFilePathRef}/>
            </div>
        </div>
    )
}