import sys
import json

from ifcWriter import IfcWriter


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

def create_ifc_test(output_file):
    """
    Test function to generate an IFC file with predefined data.

    :param json_data: A dictionary for test purposes, though it is not dynamically used in this function.
                      Example: {"storeys": {"1F": 0.0, "2F": 3.0, "3F": 6.0}}
    :param output_file: The file path where the test IFC file will be saved.
                        Example: "test_output.ifc"
    :return: The path to the saved IFC file.

    This method serves as a test or example implementation. Instead of dynamically processing
    `json_data`, it creates a fixed set of storeys and writes them to an IFC file.

    Example:
        writer.create_storeys({'1F': 0.0, '2F': 3.0, '3F': 6.0})

    Use this function to verify that the `IfcWriter` class and `create_storeys` logic are functioning
    correctly before implementing the dynamic parsing in `create_ifc_from_json`.
    """
    writer = IfcWriter()

    # Fixed set of storeys for testing
    writer.create_storeys({'1F': 0.0, '2F': 3.0, '3F': 6.0})

    writer.save(output_file)
    return output_file

# Message handling loop for continuous processing
while True:
    line = sys.stdin.readline()
    if not line:
        break

    # Process the incoming message
    response = handle_message(line.strip())

    # Output the response as JSON
    print(json.dumps(response))
    sys.stdout.flush()