import { MappableItem } from "../mappableItem";

export class MappableIfcBuildingStorey extends MappableItem {
    constructor(data: any) {
        super(data);
        this.requiredParams = new Set(["name", "height"]);
    }

    protected validateTypes(data: any): boolean {
        return (
            typeof data.name === "string" && 
            typeof data.height === "number"
        );
    }
}