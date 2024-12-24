import { MappableItem } from "../mappableItem";

export class MappableIfcBeam extends MappableItem {
    constructor(data: any) {
        super(data, new Set(["startPt", "endPt", "height", "targetStorey"]));
        if(this.isValid) {
            this.startPt = data.userArgs.startPt;
            this.endPt = data.userArgs.endPt;
            this.height = data.userArgs.height;
            this.targetStorey = data.userArgs.targetStorey;
        }
    }

    protected startPt: Array<number> | undefined;
    protected endPt: Array<number> | undefined;
    protected height: number | undefined;
    protected targetStorey: string | undefined;

    protected validateTypes(data: any): boolean {
        return (
            Array.isArray(data.startPt) && data.startPt.every((item: any) => typeof item === "number") && data.startPt.length === 3 &&
            Array.isArray(data.endPt) && data.endPt.every((item: any) => typeof item === "number") && data.startPt.length === 3 &&
            typeof data.height === "number" &&
            typeof data.targetStorey === "string"
        );
    }
}