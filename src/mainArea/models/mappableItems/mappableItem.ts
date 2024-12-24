export abstract class MappableItem {
    protected requiredParams: Set<string>;
    protected mappingArgs: Set<string> = new Set();
    readonly isValid: boolean;

    constructor(data: any) {
        this.requiredParams = new Set();
        this.isValid = this.validate(data);
        if (this.isValid) {
            this.mappingArgs = new Set(this.requiredParams);
        }
    }

    protected abstract validateTypes(data: any): boolean;

    validate(data: any): boolean {
        const hasRequiredKeys = Array.from(this.requiredParams).every(param=> Object.keys(data).includes(param));
        if (!hasRequiredKeys) {
            return false;
        }
        
        return this.validateTypes(data);
    }
}