import { IpcMain } from "electron";
import { AppController } from "../../mainArea/appController";
import path from 'path';
import os from 'os';

function getDesktopPath(): string {
    // 사용자 홈 디렉토리와 Desktop 디렉토리를 결합하여 경로 반환
    return path.join(os.homedir(), 'Desktop');
}

export function setIPCElectronTestHandler(ipcMain: IpcMain) {
    ipcMain.handle('electron-test', async () => {
        const randomWords = [
            "apple",
            "mountain",
            "ocean",
            "river",
            "forest",
            "sky",
            "breeze",
            "cloud",
            "sunlight",
            "flower"
        ];

        const index = Math.trunc(Math.random()*10);

        return randomWords[index];
    })

    ipcMain.handle('electron-python-test', async (_, message: string) => {
        const handler = AppController.getInstance().getPythonProcessHandler();
        (async () => {
            try {
                // Python 프로세스 시작
                handler.start();

                // Path
                const desktopPath = getDesktopPath();
                const outputFile = path.join(desktopPath, 'output.ifc');
        
                // JSON 데이터를 기반으로 IFC 파일 생성 요청
                const jsonData = {
                    action: "create_ifc_test",
                    project_name: "My Building Project",
                    site_name: "my_site",
                    elements: [
                        { type: "IfcWall", name: "Main Wall" },
                        { type: "IfcDoor", name: "Entrance Door" },
                        { type: "IfcWindow", name: "Living Room Window" },
                    ],
                    output_file: outputFile
                };
        
                const response = await handler.sendMessage(jsonData);
        
                // Python 응답 처리
                console.log(`------Python Response------`);
                console.log(response);
                console.log(`---------------------------`);
        
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
            }
        })();
    });
}