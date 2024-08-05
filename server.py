import os
import asyncio
import websockets
from dotenv import load_dotenv
from actualAI import get_groq_response

# Load environment variables from .env file
load_dotenv()

def localhost(port): return {f"http://localhost:{port}", f"http://127.0.0.1:{port}"}

def strip_link(site):return {site, site+"/"}
# Allowed origins
ALLOWED_ORIGINS = localhost(8000)|{"https://nextgensell.com","https://nextgensell.com/","https://www.nextgensell.com/RetailBackOffice/chatbot"} 

# Memory storage for each WebSocket connection
memory_store = {}

async def handler(websocket, path):
    origin = websocket.request_headers.get('Origin')
    if origin not in ALLOWED_ORIGINS:
        await websocket.close(code=1008, reason='Forbidden origin')
        print(f"Connection from forbidden origin: {origin}")
        return
    print(f"Connection from: {origin}")

    # Initialize memory for this WebSocket connection
    memory_store[websocket] = []

    try:
        async for message in websocket:
            print(f"Received message: {message}")

            # Store message in memory for this WebSocket
            memory_store[websocket].append(message)

            # Use the memory context when getting the response
            response = get_groq_response(message, memory_store[websocket])
            await websocket.send(response)

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")

    finally:
        # Clean up memory for this WebSocket connection
        if websocket in memory_store:
            del memory_store[websocket]
        print("Memory for this connection cleared.")


start_server = websockets.serve(handler, "0.0.0.0", 8765)

# Start the server
asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server started on ws://0.0.0.0:8765")
asyncio.get_event_loop().run_forever()
