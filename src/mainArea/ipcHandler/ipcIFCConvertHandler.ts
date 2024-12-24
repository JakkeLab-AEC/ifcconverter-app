import { IpcMain } from "electron";
import { AppController } from "../appController/appController";
import path from 'path';
import os from 'os';

function getDesktopPath(): string {
    // 사용자 홈 디렉토리와 Desktop 디렉토리를 결합하여 경로 반환
    return path.join(os.homedir(), 'Desktop');
}

export function setIPCElectronIFCHandler(ipcMain: IpcMain) {
    ipcMain.handle('ifc-create', async (_, message: string) => {
        const handler = AppController.getInstance().getPythonProcessHandler();
        
        (async () => {
            try {
                // Python 프로세스 시작
                handler.start();

                // Path
                const outputFile = AppController.getInstance().getDataStore().getIfcPath();
                if(outputFile === null) {
                    throw new Error('IFC output file path is not set.');
                }
        
                // JSON 데이터를 기반으로 IFC 파일 생성 요청
                const jsonData = {
                    "header": {
                        "action": "create_ifc",
                        "project_name": "My Building Project",
                        "site_name": "my_site",
                    },
                    "entities": {
                        "elements": [],
                        "output_file": outputFile
                    },
                };
                
                const response = await handler.sendMessage(jsonData);
                // Python 메시지의 response_type 확인
                if(!Object.keys(response).includes('status')) {
                    // Python 프로세스 종료
                    handler.stop();
                    return;
                }

                if (response.status === 'success') {
                    console.log(`IFC File created at: ${response.file}`);
                } else {
                    console.error(`Error: ${response.message}`);
                }
            } catch (error) {
                console.error('Error during Python IPC communication:', error);
            } finally {
                // Python 프로세스 종료
                handler.stop();
                return;
            }
        })();
    });
}