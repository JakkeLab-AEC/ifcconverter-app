import sys
import json

from src.mainPython.ifcWriter import IfcWriter


def handle_message(message):
    try:
        request = json.loads(message)
        action = request.get('action')

        if action== "greet":
            return {"status": "success", "message": f"Hello, {request.get('name', 'Guest')}!"}

        elif action == "create_ifc":
            # JSON 데이터에서 파일 경로와 IFC 작성 요청 처리
            json_data = request.get("data", {})
            output_file = request.get("output_file", "output.ifc")

            # IFC 파일 생성
            try:
                file_path = create_ifc_from_json(json_data, output_file)
                return {"status": "success", "message": "IFC file created", "file": file_path}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        else:
            return {"status": "error", "message": "Unknown action"}

    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON format"}

def create_ifc_from_json(json_data, output_file):
    """
   JSON 데이터를 바탕으로 IFC 파일을 생성합니다.
   """
    writer = IfcWriter()
    writer.set_project_info(json_data.get("project_name", "Default Project"))

    for element in json_data.get("elements", []):
        writer.add_entity(
            entity_type=element.get("type", "IfcBuilding"),
            name=element.get("name", "Unnamed Element")
        )

    writer.save(output_file)
    return output_file

# 메시지 처리 루프
while True:
    line = sys.stdin.readline()
    if not line:
        break

    response = handle_message(line.strip())

    print(json.dumps(response))
    sys.stdout.flush()