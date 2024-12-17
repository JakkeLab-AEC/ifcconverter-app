import sys
import json

from ifcWriter import IfcWriter
import ifcopenshell.util.selector

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
        action = request.get('action')

        if action== "greet":
            return {"status": "success", "message": f"Hello, {request.get('name', 'Guest')}!"}

        elif action == "create_ifc":
            json_data = request.get("data", {})
            output_file = request.get("output_file", "output.ifc")

            try:
                # Create IFC file and return the file path
                file_path = create_ifc_from_json(json_data, output_file)
                return {"status": "success", "message": "IFC file created", "file": file_path}
            except Exception as e:
                # Return an error if IFC creation fails
                return {"status": "error", "message": str(e)}

        elif action == "create_ifc_test":
            output_file = request.get("output_file", "output.ifc")

            try:
                file_path = create_ifc_test(output_file)
                return {"status": "success", "message": "IFC test file created", "file": file_path}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        else:
            return {"status": "error", "message": "Unknown action"}

    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON format"}

def create_ifc_from_json(json_data, output_file):
    """
    Generates an IFC file based on the provided JSON data.

    :param json_data: A dictionary containing the data required to construct the IFC file.
                      The structure and required keys depend on the application's implementation.
                      Example: {"storeys": {"1F": 0.0, "2F": 3.0, "3F": 6.0}}
    :param output_file: The file path where the IFC file will be saved.
                        Example: "output.ifc"
    :return: The path to the saved IFC file.

    This method is the main function intended for production use. It takes dynamic `json_data`
    input and uses it to construct an IFC file. The actual implementation for processing `json_data`
    needs to be written in this function.

    Note: This function currently acts as a placeholder and requires codes for parsing and handling
    `json_data` to generate the appropriate IFC structure.
    """

    writer = IfcWriter()

    # Codes will be written here to process `json_data` dynamically

    writer.save(output_file)
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

        # Output the response as JSON
        print(json.dumps(response))
        sys.stdout.flush()

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

    # column1 = writer.ifcSharedElementDataUtil.create_column(
    #     profile_name="PROF_COL_I_300x300",
    #     col_type_name="COL_I_300x300",
    #     target_storey_name="1F",
    #     coordinate=(1., 1.),
    #     base_offset=0.0,
    #     height=2.,
    #     rotation_degree=30,
    #     profile_arg={"w": 0.3, "h": 0.3, "tw": 0.01, "tf": 0.015, "r": 0.01}
    # )

    # writer.ifcResourceEntityUtil.create_material(
    #     name="STEEL_RED",
    #     rgba={"r": 255, "g": 120, "b": 120, "a": 0.8},
    # )
    #
    # writer.ifcResourceEntityUtil.assign_material(
    #     material_name="STEEL_RED",
    #     target_objects=[column1]
    # )
    #
    # writer.ifcResourceEntityUtil.assign_material(
    #     material_name="STEEL_RED",
    #     target_objects=[writer.element_types["column_types"]["COL_I_300x300"]["Entity"]]
    # )
    #
    # writer.ifcResourceEntityUtil.create_trimmed_curve()

    writer.ifcResourceEntityUtil.create_arbitrary_closed_profile_def(

    )

    writer.save(output_file)

    return output_file

# Test mode or default behavior
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode: Run the script with a predefined JSON input
        print("Running in test mode...")
        test_input = {
            "action": "create_ifc_test",
            "output_file": f"{sys.argv[2]}/test_type2.ifc",
            "json_file": f"{sys.argv[2]}/test_output.json"
        }
        response = handle_message(json.dumps(test_input))
        create_ifc_test(test_input['output_file'])
        print(json.dumps(response, indent=4))  # Pretty-print the response
    else:
        # Default behavior: Continuous message loop
        message_loop()