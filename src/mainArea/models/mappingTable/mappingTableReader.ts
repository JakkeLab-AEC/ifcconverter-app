import { IfcBeamArgs, IfcBuildingStoreyArgs, IfcColumnArgs, MappableIfcClasses, MappingTableDefinition, UserArgs, UserArgsMap } from "./mappingTableDefinition";

export class MappingTableReader {
    constructor() {
        this.mappingRule = new Map();
        this.userKeyMap = new Map();
    }
    
    readMappingJson(data: any): boolean {
        try {
            const parsedData: MappingTableDefinition = JSON.parse(data);
            const validationResult = this.validate(parsedData);

            if (validationResult) {
                this.storeMappingRules(parsedData);
            }
            return validationResult;
        } catch (error) {
            console.error("Failed to parse JSON:", error);
            return false;
        }
    }

    private validate(data: MappingTableDefinition): boolean {
        try {
            for (const [key, value] of Object.entries(data.mappingEntity)) {
                const mappableClass = key as MappableIfcClasses;

                switch (mappableClass) {
                    case MappableIfcClasses.IfcColumn:
                        this.validateIfcColumn(value.userArgs as IfcColumnArgs);
                        break;

                    case MappableIfcClasses.IfcBeam:
                        this.validateIfcBeam(value.userArgs as IfcBeamArgs);
                        break;

                    case MappableIfcClasses.IfcBuildingStorey:
                        this.validateIfcBuildingStorey(value.userArgs as IfcBuildingStoreyArgs);
                        break;

                    default:
                        throw new Error(`Unsupported IFC class: ${mappableClass}`);
                }
            }

            return true;
        } catch (error) {
            console.error(error);
            return false;
        }
    }

    private validateIfcColumn(args: IfcColumnArgs): void {
        if (!args.coordinate || !args.height || !args.rotation || !args.targetStorey) {
            throw new Error(`Invalid IfcColumn arguments: ${JSON.stringify(args)}`);
        }
    }

    private validateIfcBeam(args: IfcBeamArgs): void {
        if (!args.startPt || !args.endPt || !args.height || !args.targetStorey) {
            throw new Error(`Invalid IfcBeam arguments: ${JSON.stringify(args)}`);
        }
    }

    private validateIfcBuildingStorey(args: IfcBuildingStoreyArgs): void {
        if (!args.name || !args.height) {
            throw new Error(`Invalid IfcBuildingStorey arguments: ${JSON.stringify(args)}`);
        }
    }

    private mappingRule: Map<MappableIfcClasses, UserArgs<MappableIfcClasses>>;
    private userKeyMap: Map<string, MappableIfcClasses>;

    private storeMappingRules(data: MappingTableDefinition): void {
        for (const [key, value] of Object.entries(data.mappingEntity)) {
            const mappableClass = key as MappableIfcClasses;
            this.setMappingRule(mappableClass, value as UserArgs<MappableIfcClasses>);
        }
    }

    setMappingRule(ifcClass: MappableIfcClasses, userArg: UserArgs<MappableIfcClasses>): void {
        this.mappingRule.set(ifcClass, userArg);
        this.userKeyMap.set(userArg.userKey, ifcClass);
    }

    getMappingRule(ifcClass: MappableIfcClasses): UserArgs<MappableIfcClasses> | undefined {
        return this.mappingRule.get(ifcClass);
    }

    getMappingRuleByUserKey(userKey: string): UserArgs<MappableIfcClasses> | undefined {
        const ruleKey = this.userKeyMap.get(userKey)
        if(ruleKey) {
            return this.mappingRule.get(ruleKey)
        }
    }

    getMappableIfcClass(userKey: string): MappableIfcClasses | undefined {
        return this.userKeyMap.get(userKey)
    }
}