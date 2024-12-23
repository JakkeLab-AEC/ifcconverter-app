import { IfcBeamArgs, IfcBuildingStoreyArgs, IfcColumnArgs, MappingTableDefinition, UserArgsMap } from "./mappingTableDefinition";

export class MappingTableReader {
    constructor() {
        
    }
    
    readMappingJson(data: any): void {
        const parsedData = JSON.parse(data);
        const validationResult = this.validate(parsedData);
        console.log(`Validation : ${validationResult}`);
    }

    private validate(data: MappingTableDefinition): boolean {
        try {
            for (const [key, value] of Object.entries(data.mappingEntity)) {
                const mappableClass = key as keyof UserArgsMap;
                
                if (mappableClass === "IfcColumn") {
                    const args: IfcColumnArgs = value.userArgs as IfcColumnArgs;
                    if (!args.coordinate || !args.height || !args.rotation || !args.targetStorey) {
                        throw new Error(`Invalid args for ${mappableClass}`);
                    }
                }

                if (mappableClass === "IfcBeam") {
                    const args: IfcBeamArgs = value.userArgs as IfcBeamArgs;
                    if (!args.startPt || !args.endPt || !args.height || !args.targetStorey) {
                        throw new Error(`Invalid args for ${mappableClass}`);
                    }
                }

                if (mappableClass === "IfcBuildingStorey") {
                    const args: IfcBuildingStoreyArgs = value.userArgs as IfcBuildingStoreyArgs;
                    if (!args.name || !args.height ) {
                        throw new Error(`Invalid args for ${mappableClass}`);
                    }
                }
            }
            
            return true;
        } catch (error) {
            console.error(error);
            return false;
        }
    }
}