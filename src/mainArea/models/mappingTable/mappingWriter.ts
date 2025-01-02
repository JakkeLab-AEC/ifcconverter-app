import { AppController } from "../../../mainArea/appController/appController";
import { MappableIfcColumn } from "../mappableItems/entities/mappableColumn";
import { MappableIfcBeam } from "../mappableItems/entities/mappableIfcBeam";
import { MappableIfcBuildingStorey } from "../mappableItems/entities/mappableIfcBuildingStorey";
import { MappableItem } from "../mappableItems/mappableItem";
import { MappableIfcClasses } from "./mappingTableDefinition";
import { MappingTableReader } from "./mappingTableReader"

export class MappingWriter {
    constructor() {
        this.mappedItem = [];
        this.unmappedItem = [];
    }

    private mappedItem: Array<MappableItem>
    private unmappedItem: Array<{entity: any, reason: string}>;

    createMappedItem (item: any, mappingTableReader: MappingTableReader):{result: boolean, message?: string} {
        const mappingRule = mappingTableReader.getMappingRuleByUserKey(item.userKey);
        if(!mappingRule) {
            this.unmappedItem.push({ entity: item, reason: "Can't find matching rule." });
            return {result: false, message: "Can't find matching rule."};
        }
    
        const keysFromItem = Object.keys(item.userArgs)
        const keysFromMappingRule = Object.values(mappingRule.userArgs)

        const allKeysIncluded = keysFromMappingRule.every((key) => keysFromItem.includes(key));
        if (!allKeysIncluded) {
            this.unmappedItem.push({ entity: item, reason: "Some required keys are not included." });
            return { result: false, message: "Some required keys are not included." };
        }

        const transformedArgs: any = {};
        for (const [internalKey, userKey] of Object.entries(mappingRule.userArgs)) {
            if (item.userArgs[userKey] !== undefined) {
                transformedArgs[internalKey] = item.userArgs[userKey];
            }
        }
        
        switch (mappingTableReader.getMappableIfcClass(item.userKey)) {
            case MappableIfcClasses.IfcBuildingStorey: {
                const entity = new MappableIfcBuildingStorey({ userKey: item.userKey, userArgs: transformedArgs });
                if (entity.isValid) {
                    this.mappedItem.push(entity);
                    return { result: true };
                } else {
                    this.unmappedItem.push({ entity: item, reason: "Type validation failed." });
                    return { result: false, message: "Type validation failed." };
                }
            }
    
            case MappableIfcClasses.IfcColumn: {
                const entity = new MappableIfcColumn({ userKey: item.userKey, userArgs: transformedArgs });
                if (entity.isValid) {
                    this.mappedItem.push(entity);
                    return { result: true };
                } else {
                    this.unmappedItem.push({ entity: item, reason: "Type validation failed." });
                    return { result: false, message: "Type validation failed." };
                }
            }
    
            case MappableIfcClasses.IfcBeam: {
                const entity = new MappableIfcBeam({ userKey: item.userKey, userArgs: transformedArgs });
                if (entity.isValid) {
                    this.mappedItem.push(entity);
                    return { result: true };
                } else {
                    this.unmappedItem.push({ entity: item, reason: "Type validation failed." });
                    return { result: false, message: "Type validation failed." };
                }
            }
    
            default: {
                this.unmappedItem.push({ entity: item, reason: "Unsupported Item." });
                return { result: false, message: "Unsupported Item." };
            }
        }
    }

    getMappedItem():Array<MappableItem> {
        return this.mappedItem;
    }

    getUnmappedItem():Array<{entity: any, reason: string}> {
        return this.unmappedItem;
    }

    exportAsJSON():Array<Object> {
        return this.mappedItem.map(item => item.export());
    }

    dispatchData(): {mappedItems: Array<any>, unmappedItems: Array<any>} {
        this.mappedItem = [];
        this.unmappedItem = [];
        const writer = AppController.getInstance().getDataStore().getMappingWriter();
        const reader = AppController.getInstance().getDataStore().getMappingTableReader();
        const datas = AppController.getInstance().getDataStore().getTargetFileData() as Array<Object>;

        for(const data of datas) {
            writer.createMappedItem(data, reader);
        }

        const result = {
            mappedItems: writer.exportAsJSON(),
            unmappedItems: [...writer.unmappedItem]
        }

        AppController.getInstance().getDataStore().resetMappingWriter();

        return result;
    }
}