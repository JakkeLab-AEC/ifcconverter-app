import { MappableItem } from "../mappableItem";

export class MappableIfcColumn extends MappableItem {
    constructor(data: any) {
        super(data);
        this.requiredParams = new Set(["coordinate", "height", "rotation", "targetStorey"]);
    }

    protected validateTypes(data: any): boolean {
        return (
            Array.isArray(data.coordinate) && data.coordinate.every((item: any) => typeof item === "number") && data.coordinate.length === 2 &&
            typeof data.height === "number" &&
            typeof data.rotation === "number" &&
            typeof data.targetStorey === "string"
        );
    }
}