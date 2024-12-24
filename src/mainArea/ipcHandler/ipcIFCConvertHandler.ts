import { IpcMain } from "electron";
import { AppController } from "../appController/appController";

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

    ipcMain.handle('ifc-mapping-test', async (_) => {
        const writer = AppController.getInstance().getDataStore().getMappingWriter();
        const reader = AppController.getInstance().getDataStore().getMappingTableReader();
        const datas = AppController.getInstance().getDataStore().getTargetFileData() as Array<Object>;
        for(const data of datas) {
            const jobResult = writer.createMappedItem(data, reader);
            console.log(jobResult);
        }

        console.log(writer.getMappedItem());
        console.log(writer.getUnmappedItem());
    });
}