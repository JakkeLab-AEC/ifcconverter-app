import { MappableItem } from "../mappableItem";

export class MappableColumn extends MappableItem {
    constructor(data: any) {
        super(data);
        this.requiredParams = new Set(new Set(["coordinate", "height", "rotation", "targetStorey"]));
    }
}