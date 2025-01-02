import { MappableIfcClasses } from "../../mappingTable/mappingTableDefinition";
import { MappableItem } from "../mappableItem";

export class MappableIfcBuildingStorey extends MappableItem {
    constructor(data: any) {
        super(data, new Set(["name", "height"]));
        if(this.isValid) {
            this.height = data.userArgs.height;
            this.name = data.userArgs.name;
        }
    }

    protected name: string | undefined;
    protected height: number | undefined;

    protected validateTypes(data: any): boolean {
        return (
            typeof data.name === "string" && 
            typeof data.height === "number"
        );
    }

    export(): Object {
        return {
            ifcClass: MappableIfcClasses.IfcBuildingStorey,
            name: this.name,
            height: this.height
        }
    }
}