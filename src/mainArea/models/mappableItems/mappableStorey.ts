import { MappableItem } from "../mappableItem";

export class MappableStorey extends MappableItem {
    constructor(data: any) {
        super(data);
        this.requiredParams = new Set(["storeyName", "height"]);
    }
}