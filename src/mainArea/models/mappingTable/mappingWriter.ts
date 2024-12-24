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
            this.unmappedItem.push(item);
            return {result: false, message: "Can't find matching rule."};
        }
    
        const keysFromItem = Object.keys(item)
        const keysFromMappingRule = Object.values(mappingRule.userArgs)
    
        const allKeysIncluded = keysFromMappingRule.every(key => keysFromItem.includes(key));
        if(!allKeysIncluded) {
            this.unmappedItem.push(item);
            return {result: false, message: "Some requied keys are not included."};
        }
        
        switch(mappingTableReader.getMappableIfcClass(item.userKey)) {
            case MappableIfcClasses.IfcBuildingStorey: {
                const entity = new MappableIfcBuildingStorey(item);
                if(entity.isValid) {
                    this.mappedItem.push(entity);
                    return {result: true}
                } else {
                    const unmappedItemWrapping = {entity: item, reason: "Type validation failed."}
                    this.unmappedItem.push(unmappedItemWrapping);
                    return {result: false, message: "Type validation failed."}
                }
            }
            
            case MappableIfcClasses.IfcColumn: {
                const entity = new MappableIfcColumn(item);
                if(entity.isValid) {
                    this.mappedItem.push(entity);
                    return {result: true}
                } else {
                    const unmappedItemWrapping = {entity: item, reason: "Type validation failed."}
                    this.unmappedItem.push(unmappedItemWrapping);
                    return {result: false, message: "Type validation failed."}
                }
            }

            case MappableIfcClasses.IfcBeam: {
                const entity = new MappableIfcBeam(item);
                if(entity.isValid) {
                    this.mappedItem.push(entity);
                    return {result: true}
                } else {
                    const unmappedItemWrapping = {entity: item, reason: "Type validation failed."}
                    this.unmappedItem.push(unmappedItemWrapping);
                    return {result: false, message: "Type validation failed."}
                }
            }

            default: {
                return {result: false, message: "Unsupported Item."}
            }
        }
    }
}