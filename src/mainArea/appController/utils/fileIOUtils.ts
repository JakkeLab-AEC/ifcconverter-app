import { dialog } from "electron";
import { MappingTableReader } from "../../models/mappingTable/mappingTableReader";
import fs from 'fs';
import { AppController } from "../appController";

export const loadJSONWithDialog = async () => {
    const dialogResult = await dialog.showOpenDialog({
        title: "매핑 테이블 불러오기",
        filters: [
            {name: "JSON", extensions: ['json']}
        ],
    })
    
    if(!dialogResult.canceled) {
        const reader = new MappingTableReader()
        const fileContent = await fs.promises.readFile(dialogResult.filePaths[0], 'utf-8');
        if(reader.readMappingJson(fileContent)) {
            AppController.getInstance().getDataStore().registerMappingTableReader(reader);
            return {result: true, path: dialogResult.filePaths[0]}
        } else {
            return {result: false, message: "Invalid mapping table.", errorCode: "Invalid"}
        }
    } else {
        return {result: false, message: "User canceled setting the path.", errorCode: "Canceled"}
    }
}

export const loadTargetFileWithDialog = async () => {
    const dialogResult = await dialog.showOpenDialog({
        title: "변환할 파일 불러오기",
        filters: [
            {name: "JSON", extensions: ['json']}
        ],
    })

    if(!dialogResult.canceled) {
        const fileContent = await fs.promises.readFile(dialogResult.filePaths[0], 'utf-8');
        try {
            const parsedData = JSON.parse(fileContent);
            console.log(parsedData);
            AppController.getInstance().getDataStore().setTargetFilePath(dialogResult.filePaths[0]);
            AppController.getInstance().getDataStore().setTargetFileData(parsedData);

            return {result: true, path: dialogResult.filePaths[0]}
        } catch (error) {
            return {result: false, message: "Invalid JSON file", errorCode: "Invalid"}
        }        
    } else {
        return {result: false, message: "User canceled setting the path.", errorCode: "Canceled"}
    }
}

export const setIfcFileWithDialog = async () => {
    const setPathDialog = await dialog.showSaveDialog({
        title: "IFC 파일 저장",
        defaultPath: "output.ifc",
        filters: [
            { name: "IFC file", extensions: ["ifc"] },
        ],
    });

    if(!setPathDialog.canceled) {
        AppController.getInstance().getDataStore().setIfcPath(setPathDialog.filePath);
        return {result: true, path: setPathDialog.filePath};
    } else {
        return {result: false, message: "User canceled setting the path."};
    }
}