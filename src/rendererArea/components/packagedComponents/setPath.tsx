import React, { useRef } from "react";

interface SetPathProps {
    label: string,
    path: string,
    onClickLoadPath: () => void
}

export const SetPath:React.FC<SetPathProps> = ({label, path, onClickLoadPath}) => {   
    return (
        <div className="flex flex-row gap-2">
            <div className="flex font-bold w-[100px]">
                {label}
            </div>
            <div className="flex flex-grow">
                <input type="text" className="border w-full rounded-md" readOnly={true} value={path}/>
            </div>
            <button className="w-[48px] border rounded-md" onClick={onClickLoadPath}>
                설정
            </button>
        </div>
    )
}