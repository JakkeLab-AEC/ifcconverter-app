export abstract class MappableItem {
    protected requiredParams: Set<string>;
    protected mappingArgs: Set<string> = new Set();
    readonly isValid: boolean;

    constructor(data: any) {
        this.requiredParams = new Set();
        this.isValid = this.validate(data);
        if (this.isValid) {
            this.mappingArgs = new Set(this.requiredParams); // 매핑 인자 설정
        }
    }

    validate(data: any): boolean {
        return Array.from(this.requiredParams).every(param => Object.keys(data).includes(param));
    }
}