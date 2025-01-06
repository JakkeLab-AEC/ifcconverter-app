import sys
import os
import json

current_file_path = os.path.abspath(__file__)

project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
sys.path.append(project_root)

from writer import IfcWriter
from printer import print_response

def handle_message(message) -> dict:
    """
    Processes incoming messages and performs actions based on the request.

    :param message: A JSON string representing the client's request.
                    Example: {"action": "greet", "name": "Alice"}
    :return: A dictionary with the status and the result of the requested action.
             Example: {"status": "success", "message": "Hello, Alice!"}

    Possible actions:
    - "greet": Returns a greeting message. Use for IPC test.
    - "create_ifc": Generates an IFC file based on the provided JSON data.
    - Unknown actions or invalid JSON format will return an error response.
    """
    try:
        request = json.loads(message)
        action = request.get('header').get('action')

        if action == "pythonTest":
            return {"status":"success","message":f"Hello, {request.get('name', 'Guest')}!"}

        elif action == "create_ifc":
            entities = request.get("entities")
            output_file = request.get("header").get("ifcFilePath")

            try:
                file_path = create_ifc_from_json(entities, output_file)
            except Exception as e:
                print_response(action="system", result=False, message=str(e))

        elif action == "create_ifc_test":
            output_file = request.get("output_file", "output.ifc")

            try:
                file_path = create_ifc_test(output_file)
                return {"status":"success", "message":"IFC test file created", "filePath": file_path}
            except Exception as e:
                return {"status":"error", "message": str(e)}
        else:
            return {"response_type": "unknown_action", "status": "error", "message": "Unknown action"}

    except json.JSONDecodeError:
        return {"response_type": "invalid_message", "status": "error", "message": "Invalid JSON format"}

def create_ifc_from_json(entities, output_file):
    """
    Generates an IFC file based on the provided JSON data.
    """
    writer = IfcWriter("IFC2x3")
    for entity in entities:
        ifc_class = entity['ifcClass']
        try:
            if ifc_class == 'IfcBuildingStorey':
                writer.ifcCoreDataUtil.create_storey(
                    name=entity['name'],
                    elevation=float(entity['height'])
                )
                print_response(action="writingEntity", entity_type=ifc_class, result=True)
            elif ifc_class == 'IfcColumn':
                coordinate = (float(entity['coordinate'][0]), float(entity['coordinate'][1]))
                writer.ifcSharedElementDataUtil.create_column(
                    profile_name="H300x300",
                    col_type_name="COL-H300x300",
                    target_storey_name=entity['targetStorey'],
                    height=float(entity['height']),
                    rotation_degree=float(entity['rotation']),
                    coordinate=coordinate,
                    profile_arg={"w": 0.3, "h": 0.3, "tw": 0.01, "tf": 0.015, "r": 0.01}
                )
                print_response(action="writingEntity", entity_type=ifc_class, result=True)
            elif ifc_class == 'IfcBeam':
                pt_start = (float(entity['startPt'][0]), float(entity['startPt'][1]))
                pt_end = (float(entity['endPt'][0]), float(entity['endPt'][1]))
                writer.ifcSharedElementDataUtil.create_beam(
                    profile_name="H300x300",
                    beam_type_name="BEAM-H300x300",
                    target_storey_name=entity['targetStorey'],
                    pt_start=pt_start,
                    pt_end=pt_end,
                    rotation_degree=float(entity['rotation']),
                    z_offset=float(entity['height']),
                    profile_arg={"w": 0.3, "h": 0.3, "tw": 0.01, "tf": 0.015, "r": 0.01}
                )
                print_response(action="writingEntity", entity_type=ifc_class, result=True)
            elif ifc_class == "IfcWallStandardCase":
                pt_start = (float(entity['startPt'][0]), float(entity['startPt'][1]))
                pt_end = (float(entity['endPt'][0]), float(entity['endPt'][1]))
                writer.ifcSharedElementDataUtil.create_wall_single(
                    wall_type_name=f"WAL_T{entity['thickness']}",
                    target_storey_name=entity['targetStorey'],
                    pt_start=pt_start,
                    pt_end=pt_end,
                    z_offset=float(entity['zOffset']),
                    wall_thickness=float(entity['thickness']),
                    wall_height=float(entity['height'])
                )
                print_response(action="writingEntity", entity_type=ifc_class, result=True)
            else:
                print_response(action="writingEntity", result=False, entity_type=ifc_class, message="Not supported IfcClass.")
                sys.stdout.flush()
        except Exception as e:
            print_response(action="writingEntity", result=False, entity_type=ifc_class, message=str(e))

        sys.stdout.flush()

    # Codes will be written here to process `json_data` dynamically
    writer.save(output_file)
    
    print_response(action="writingFile", result=True)
    sys.stdout.flush()
    return output_file

# Message handling loop for continuous processing
def message_loop():
    """
    Continuously processes incoming messages from stdin.
    """
    while True:
        line = sys.stdin.readline()
        if not line:
            break

        # Process the incoming message
        response = handle_message(line.strip())

def create_ifc_test(output_file):
    """
    Test function to generate an IFC file with predefined data.

    :param json_data: A dictionary for test purposes, though it is not dynamically used in this function.
                      Example: {"storeys": {"1F": 0.0, "2F": 3.0, "3F": 6.0}}
    :param output_file: The file path where the test IFC file will be saved.
                        Example: "test_1.ifc"
    :return: The path to the saved IFC file.

    This method serves as a test or example implementation. Instead of dynamically processing
    `json_data`, it creates a fixed set of storeys and writes them to an IFC file.

    Example:
        writer.create_storeys({'1F': 0.0, '2F': 3.0, '3F': 6.0})

    Use this function to verify that the `IfcWriter` class and `create_storeys` logic are functioning
    correctly before implementing the dynamic parsing in `create_ifc_from_json`.
    """
    writer = IfcWriter(schema="IFC2x3")

    writer.ifcCoreDataUtil.create_storey(
        name="1F",
        elevation=3.
    )

    writer.ifcCoreDataUtil.create_storey(
        name="2F",
        elevation=6.
    )

    writer.ifcCoreDataUtil.create_storey(
        name="3F",
        elevation=9.
    )

    # beam1 = writer.ifcSharedElementDataUtil.create_beam(
    #     profile_name="BEAM_I_300x300",
    #     beam_type_name="BEAM_I_300x300",
    #     target_storey_name="1F",
    #     pt_start=(0., 0.),
    #     pt_end=(4., 3.),
    #     rotation_degree=30,
    #     z_offset=-1.,
    #     profile_arg={"w": 0.3, "h": 0.3, "tw": 0.01, "tf": 0.015, "r": 0.01}
    # )
    #
    # beam2 = writer.ifcSharedElementDataUtil.create_beam(
    #     profile_name="BEAM_I_300x300",
    #     beam_type_name="BEAM_I_300x300",
    #     target_storey_name="1F",
    #     pt_start=(4., 4.),
    #     pt_end=(7., 7.),
    #     rotation_degree=30,
    #     z_offset=-1.,
    #     profile_arg={"w": 0.3, "h": 0.3, "tw": 0.01, "tf": 0.015, "r": 0.01}
    # )
    #
    # writer.ifcResourceEntityUtil.create_material(
    #     name="STEEL_RED",
    #     rgba={"r": 255, "g": 120, "b": 120, "a": 0.8},
    # )
    #
    # writer.ifcResourceEntityUtil.assign_material(
    #     material_name="STEEL_RED",
    #     target_objects=[beam1]
    # )
    #
    # print(writer.element_types["beam_types"])
    # writer.ifcResourceEntityUtil.assign_material(
    #     material_name="STEEL_RED",
    #     target_objects=[writer.element_types["beam_types"]["BEAM_I_300x300"]["Entity"]]
    # )

    writer.ifcSharedElementDataUtil.create_column(
        profile_name="PROF_I_300x300",
        col_type_name="COL_I_300x300",
        target_storey_name="1F",
        coordinate=(0., 0.),
        height=4.,
        rotation_degree=30.,
        profile_arg={"w": 0.3, "h": 0.3, "tw": 0.01, "tf": 0.015, "r": 0.01}
    )

    writer.ifcSharedElementDataUtil.test_extrusion()

    writer.ifcSharedElementDataUtil.create_wall_single(
        wall_type_name="W_T120",
        target_storey_name="1F",
        pt_start=(1., 1.),
        pt_end=(5., 5.),
        z_offset=-1.,
        wall_thickness=0.3,
        wall_height=3.5
    )

    writer.ifcSharedElementDataUtil.create_wall_single(
        wall_type_name="W_T120",
        target_storey_name="1F",
        pt_start=(7., 7.),
        pt_end=(15., 12.),
        z_offset=-1.,
        wall_thickness=0.3,
        wall_height=3.5
    )

    print(output_file)

    writer.save(output_file)

    return output_file

# Test mode or default behavior
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode: Run the script with a predefined JSON input
        print("Running in test mode...")
        test_input = {"header" : {
            "action": "create_ifc_test",
            "output_file": f"test_type2.ifc",
            "json_file": f"test_output.json"
        }}
        response = handle_message(json.dumps(test_input))
        create_ifc_test(test_input["header"]['output_file'])
        print(json.dumps(response, indent=4))  # Pretty-print the response
    else:
        # Default behavior: Continuous message loop
        message_loop()

