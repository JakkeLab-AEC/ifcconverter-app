import ifcopenshell
import sys
import json

def test_handle_message(message):
    try:
        request = json.loads(message)
        if request.get('action') == "greet":
            return {"status": "success", "message": f"Hello, {request.get('name', 'Guest')}!"}
        else:
            return {"status": "error", "message": "Unknown action"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON format"}

while True:
    line = sys.stdin.readline()
    if not line:
        break

    response = test_handle_message(line.strip())

    print(json.dumps(response))
    sys.stdout.flush()