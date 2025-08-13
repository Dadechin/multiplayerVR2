import asyncio
import websockets
import json
import uuid
from websockets.protocol import State
clients = {} # websocket -> player_id
player_states = {} # player_id -> latest XRPlayerState
async def handle_connection(websocket):
    player_id = str(uuid.uuid4())
    clients[websocket] = player_id
    # Send all existing players to the new player
    for pid, state in player_states.items():
        if pid != player_id:
            await websocket.send(json.dumps(state))
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"[{player_id}] {data}")
            # Save the XRPlayerState (assumes every message is a state update)
            if data.get("id") == player_id:
                player_states[player_id] = data
            # Broadcast to other clients
            for client in clients:
                if (client != websocket and client.state == State.OPEN):
                    await client.send(message)
    except websockets.exceptions.ConnectionClosed:
        print(f"[DISCONNECTED] {player_id}")
    finally:
        clients.pop(websocket, None)
        player_states.pop(player_id, None)
async def main():
    async with websockets.serve(handle_connection, "0.0.0.0", 8765):
        print("✅ WebSocket server running on ws://0.0.0.0:8765")
        await asyncio.Future()
if __name__ == "__main__":
    asyncio.run(main())