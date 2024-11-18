import asyncio
import websockets
import ifcopenshell

async def handle_request(websocket):
    async for message in websocket:
        print(f"Received: {message}")

        response = "Responsed from electron"
        await websocket.send(response)

asyncio.get_event_loop().run_until_complete(
    websockets.serve(handle_request, "localhost", 5666)
)
asyncio.get_event_loop().run_forever()