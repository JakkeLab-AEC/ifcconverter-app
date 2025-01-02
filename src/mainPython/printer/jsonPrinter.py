import json
from typing import Literal

def print_response(
        action:Literal["writingFile", "writingEntity", "system"],
        result: bool,
        entity_type: Literal["IfcBuildingStorey", "IfcColumn", "IfcBeam"]|str|None=None,
        message: str|None = None
    ) -> None:
    data = {
        "action": action,
        "result": result,
    }

    if message is not None:
        data["message"] = message

    if entity_type is not None:
        data["entityType"] = entity_type

    print(json.dumps(data, ensure_ascii=False, indent=4), flush=True, end="\n")