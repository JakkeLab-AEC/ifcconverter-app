export class DataStoreService {    
    constructor() {
        this.ifcPath = null;
    }

    private ifcPath: string|null;

    getIfcPath(): string|null {
        return this.ifcPath;
    }
    
    setIfcPath(path: string) {
        this.ifcPath = path;
    }
}