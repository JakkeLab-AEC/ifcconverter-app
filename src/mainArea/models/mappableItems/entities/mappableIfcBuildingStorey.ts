import { MappableItem } from "../mappableItem";

export class MappableIfcBuildingStorey extends MappableItem {
    constructor(data: any) {
        super(data, new Set(["name", "height"]));
        if(this.isValid) {
            console.log("---DATA---");
            console.log(data);
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
}