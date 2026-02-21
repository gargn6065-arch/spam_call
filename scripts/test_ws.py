import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/call"
    async with websockets.connect(uri) as websocket:
        messages = [
            {"text": "Hello, I am calling from your bank."},
            {"text": "We noticed some suspicious activity on your account."},
            {"text": "Please provide your OTP to verify your identity."}
        ]

        for msg in messages:
            print(f"Sending: {msg['text']}")
            await websocket.send(json.dumps(msg))
            response = await websocket.recv()
            print(f"Received: {response}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    # This script assumes the server is running
    try:
        asyncio.run(test_websocket())
    except Exception as e:
        print(f"Error: {e}")
