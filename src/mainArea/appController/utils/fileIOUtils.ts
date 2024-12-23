import { dialog } from "electron";
import { MappingTableReader } from "../../utils/mappingTable/mappingTableReader";
import fs from 'fs';

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
        reader.readMappingJson(fileContent)
    }
}