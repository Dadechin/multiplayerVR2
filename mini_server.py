import asyncio
import websockets
import json
import uuid
import sys
from websockets.protocol import State

clients = {}  # websocket -> player_id
player_states = {}  # player_id -> latest XRPlayerState

async def handle_connection(websocket):
    player_id = str(uuid.uuid4())
    clients[websocket] = player_id
    # Send all existing players to the new player
    for pid, state in player_states.items():
        if pid != player_id:
            try:
                await websocket.send(json.dumps(state))
            except websockets.exceptions.ConnectionClosed:
                break
    
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"[{player_id}] {data}")
            # Save the XRPlayerState (assumes every message is a state update)
            if data.get("id") == player_id:
                player_states[player_id] = data
            # Broadcast to other clients
            for client in list(clients.keys()):  # Create a copy to avoid modification during iteration
                if (client != websocket or True) and client.state == State.OPEN:
                    try:
                        await client.send(message)
                    except websockets.exceptions.ConnectionClosed:
                        continue
    except websockets.exceptions.ConnectionClosed:
        print(f"[DISCONNECTED] {player_id}")
    finally:
        clients.pop(websocket, None)
        player_states.pop(player_id, None)

async def main(port):
    async with websockets.serve(handle_connection, "0.0.0.0", port):
        print(f"✅ WebSocket server running on ws://0.0.0.0:{port}")
        await asyncio.Future()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mini_server.py <port>")
        sys.exit(1)
    
    port = int(sys.argv[1])
    asyncio.run(main(port))