import { MappableItem } from "../mappableItem";

export class MappableIfcBeam extends MappableItem {
    constructor(data: any) {
        super(data);
        this.requiredParams = new Set(["startPt", "endPt", "height", "targetStorey"]);
    }

    protected validateTypes(data: any): boolean {
        return (
            Array.isArray(data.startPt) && data.startPt.every((item: any) => typeof item === "number") && data.startPt.length === 3 &&
            Array.isArray(data.endPt) && data.endPt.every((item: any) => typeof item === "number") && data.startPt.length === 3 &&
            typeof data.height === "number" &&
            typeof data.targetStorey === "string"
        );
    }
}