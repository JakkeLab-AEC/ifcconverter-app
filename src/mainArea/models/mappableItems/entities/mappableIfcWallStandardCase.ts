import { MappableIfcClasses } from "../../mappingTable/mappingTableDefinition";
import { MappableItem } from "../mappableItem";

export class MappableIfcWallStandardCase extends MappableItem{
    constructor(data: any) {
        super(data, new Set(["startPt","endPt", "height", "zOffset", "thickness", "targetStorey"]))
        if(this.isValid) {
            this.startPt = data.userArgs.startPt;
            this.endPt = data.userArgs.endPt;
            this.height = data.userArgs.height;
            this.zOffset = data.userArgs.zOffset;
            this.targetStorey = data.userArgs.targetStorey;
            this.thickness = data.userArgs.thickness;
        }
    }

    protected startPt:Array<number> | undefined;
    protected endPt:Array<number> | undefined;
    protected height:number | undefined;
    protected zOffset:number | undefined;
    protected targetStorey:string | undefined;
    protected thickness:number | undefined;

    protected validateTypes(data: any): boolean {
        return (
            Array.isArray(data.startPt) && data.startPt.every((item: any) => typeof item === "number") && data.startPt.length === 2 &&
            Array.isArray(data.endPt) && data.endPt.every((item: any) => typeof item === "number") && data.startPt.length === 2 &&
            typeof data.height === "number" &&
            typeof data.zOffset === "number" &&
            typeof data.targetStorey === "string" &&
            typeof data.thickness === "number"
        );
    }
    
    export(): Object {
        return {
            ifcClass: MappableIfcClasses.IfcWallStandardCase,
            startPt: this.startPt,
            endPt: this.endPt,
            height: this.height,
            targetStorey: this.targetStorey,
            thickness: this.thickness,
            zOffset: this.zOffset
        }
    }
}