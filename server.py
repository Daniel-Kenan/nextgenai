import asyncio
import websockets
from actualAI import get_groq_response
# Allowed origins
ALLOWED_ORIGINS = {"http://127.0.0.1:5500", "https://nextgensell.com"}

async def handler(websocket, path):
    origin = websocket.request_headers.get('Origin')
    if origin not in ALLOWED_ORIGINS:
        await websocket.close(code=1008, reason='Forbidden origin')
        print(f"Connection from forbidden origin: {origin}")
        return
    print(f"Connection from: {origin}")

    try:
        async for message in websocket:
            print(f"Received message: {message}")
            await websocket.send(get_groq_response(message))
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")

start_server = websockets.serve(handler, "localhost", 8765)

# Start the server
asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server started on ws://localhost:8765")
asyncio.get_event_loop().run_forever()
