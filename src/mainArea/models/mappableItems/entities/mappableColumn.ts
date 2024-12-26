import { MappableIfcClasses } from "../../mappingTable/mappingTableDefinition";
import { MappableItem } from "../mappableItem";

export class MappableIfcColumn extends MappableItem {
    constructor(data: any) {
        super(data, new Set(["coordinate", "height", "rotation", "targetStorey"]));
        if(this.isValid) {
            this.coordinate = data.userArgs.coordinate;
            this.height = data.userArgs.height;
            this.rotation = data.userArgs.rotation;
            this.targetStorey = data.userArgs.targetStorey;
        }
    }
    
    protected coordinate: Array<number> | undefined;
    protected height: number | undefined;
    protected rotation: number | undefined;
    protected targetStorey: string | undefined;

    protected validateTypes(data: any): boolean {
        return (
            Array.isArray(data.coordinate) && data.coordinate.every((item: any) => typeof item === "number") && data.coordinate.length === 2 &&
            typeof data.height === "number" &&
            typeof data.rotation === "number" &&
            typeof data.targetStorey === "string"
        );
    }

    export(): Object {
        return {
            ifcClass: MappableIfcClasses.IfcColumn,
            coordinate: this.coordinate,
            height: this.height,
            rotation: this.rotation,
            targetStorey: this.targetStorey
        }
    }
}