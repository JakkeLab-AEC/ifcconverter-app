import { MappingWriter } from "../../models/mappingTable/mappingWriter";
import { MappingTableReader } from "../../models/mappingTable/mappingTableReader";

export class DataStoreService {    
    constructor() {
        this.ifcPath = null;
        this.targetFilePath = null;
        this.mappingTablePath = null;
        this.mappingTableReader = new MappingTableReader();
        this.mappingWriter = new MappingWriter();
        this.targetFileData = {};
    }

    private mappingTablePath: string|null;
    private targetFilePath: string|null;
    private ifcPath: string|null;
    private mappingTableReader: MappingTableReader;
    private mappingWriter: MappingWriter;
    private targetFileData: Object;

    getIfcPath(): string|null {
        return this.ifcPath;
    }
    
    setIfcPath(path: string) {
        this.ifcPath = path;
    }

    getMappingTablePath(): string|null {
        return this.mappingTablePath;
    }
    
    setMappingTablePath(path: string) {
        this.mappingTablePath = path;
    }

    getTargetFilePath(): string|null {
        return this.targetFilePath;
    }
    
    setTargetFilePath(path: string) {
        this.targetFilePath = path;
    }

    registerMappingTableReader(mappingTableReader: MappingTableReader) {
        this.mappingTableReader = mappingTableReader;
    }

    getMappingTableReader(): MappingTableReader {
        return this.mappingTableReader;
    }

    getTargetFileData(): Object {
        return this.targetFileData;
    }

    setTargetFileData(data: Object) {
        this.targetFileData = data;
    }

    resetMappingWriter() {
        this.mappingWriter = new MappingWriter();
    }

    getMappingWriter(): MappingWriter {
        return this.mappingWriter;
    }
}