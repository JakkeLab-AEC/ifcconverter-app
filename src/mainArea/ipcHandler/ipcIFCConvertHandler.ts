import { IpcMain } from "electron";
import { AppController } from "../appController/appController";

export function setIPCElectronIFCHandler(ipcMain: IpcMain) {
    // ipcMain.handle('ifc-create', async (_, message: string) => {
    //     const handler = PythonProcessHandler.instance;

    //     const { mappedItems, unmappedItems } = AppController.getInstance().getDataStore().getMappingWriter().dispatchData();
    //     const countListner = (count: number, message: string) => {
    //         IfcCreationMessageSender({
    //             totalSteps: mappedItems.length + 1,
    //             currentStep: count,
    //             message: message
    //         });
    //     };

    //     if(!handler) {
    //         return;
    //     }

    //     (async () => {
    //         try {
    //             // Python 프로세스 시작
    //             handler.start();

    //             // Path
    //             const outputFile = AppController.getInstance().getDataStore().getIfcPath();
    //             if(outputFile === null) {
    //                 throw new Error('IFC output file path is not set.');
    //             }
        
    //             // JSON 데이터를 기반으로 IFC 파일 생성 요청
    //             const jsonData = {
    //                 "header": {
    //                     "action": "create_ifc",
    //                     "projectName": "My Building Project",
    //                     "siteName": "my_site",
    //                     "ifcFilePath": outputFile
    //                 },
    //                 "entities": mappedItems
    //             };
                
    //             await handler.sendMessage(jsonData, countListner);
    //         } catch (error) {
    //             console.error('Error during Python IPC communication:', error);
    //         } finally {
    //             // Python 프로세스 종료
    //             handler.stop();
    //             return;
    //         }
    //     })();
    // });

    ipcMain.handle('ifc-mapping-test', async (_) => {
        const writer = AppController.getInstance().getDataStore().getMappingWriter();
        const reader = AppController.getInstance().getDataStore().getMappingTableReader();
        const datas = AppController.getInstance().getDataStore().getTargetFileData() as Array<Object>;
        for(const data of datas) {
            const jobResult = writer.createMappedItem(data, reader);
        }

        AppController.getInstance().getDataStore().resetMappingWriter();
    });
}