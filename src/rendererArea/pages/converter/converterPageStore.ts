import { create } from "zustand";

interface ConverterPageProps {
    pathMappingTable: string,
    pathTargetFile: string,
    pathIfcFile: string,
    currentProgress: number,
    logs: string[],
    setMappingTable:() => Promise<void>,
    setTargetFile:() => Promise<void>,
    setIfcFile:() => Promise<void>,
    setCurrentProgress:(progress: number) => void,
    pushLog: (log: string) => void,
    flushLogs: () => void,
}

export const useConverterPageStore = create<ConverterPageProps>((set, get) => ({
    pathMappingTable: "",
    pathTargetFile: "",
    pathIfcFile: "",
    currentProgress: 0,
    logs: [],
    setMappingTable: async () => {
        const jobResult = await window.electronFileIOAPI.setMappingTable();
        if(jobResult.result) {
            set(() => {
                return {
                    pathMappingTable: jobResult.path
                }
            });
        } else if (jobResult.errorCode === 'Invalid') {
            alert("유효하지 않은 매핑테이블 입니다.");
        }
    },
    setTargetFile: async () => {
        const jobResult = await window.electronFileIOAPI.setTargetFilePath();
        if(jobResult.result) {
            set(() => {
                return {
                    pathTargetFile: jobResult.path
                }
            });
        } else if (jobResult.errorCode === 'Invalid') {
            alert("유효하지 않은 변환대상 입니다.");
        }
    },
    setIfcFile: async () => {
        const jobResult = await window.electronFileIOAPI.setIfcPath();
        if(jobResult.result) {
            set(() => {
                return {
                    pathIfcFile: jobResult.path
                }
            });
        }
    },
    setCurrentProgress:(progress: number) => {
        set(() => {
            return {
                currentProgress: progress
            }
        });
    },
    pushLog: (log: string) => {
        const updatedLogs = [...get().logs];
        updatedLogs.push(log);
        set(() => {
            return {
                logs: updatedLogs
            }
        })
    },
    flushLogs: () => {
        set(() => {
            return {
                logs: []
            }
        })
    }
}));