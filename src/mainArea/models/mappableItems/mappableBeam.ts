import { MappableItem } from "../mappableItem";

export class MappableBeam extends MappableItem {
    constructor(data: any) {
        super(data);
        this.requiredParams = new Set(new Set(["startPt", "endPt", "height", "targetStorey"]));
    }
}