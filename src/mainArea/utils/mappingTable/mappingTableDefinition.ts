enum MappableIfcClasses {
    IfcBuildingStorey = "IfcBuildingStorey",
    IfcColumn = "IfcColumn",
    IfcBeam = "IfcBeam"
}

export type UserArgsMap = {
    IfcColumn: IfcColumnArgs;
    IfcBeam: IfcBeamArgs;
    IfcBuildingStorey: IfcBuildingStoreyArgs;
}

export interface IfcColumnArgs {
    coordinate: string,
    height: string,
    rotation: string,
    targetStorey: string
}

export interface IfcBeamArgs {
    startPt: string,
    endPt: string,
    height: string,
    targetStorey: string
}

export interface IfcBuildingStoreyArgs {
    name: string,
    height: string
}

export interface UserArgs<T extends MappableIfcClasses> {
    userKey: string;
    userArgs: UserArgsMap[T];
}

export interface MappingTableDefinition {
    mappingEntity: {
        [K in MappableIfcClasses]: UserArgs<K>;
    };
}