import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/call"
    async with websockets.connect(uri) as websocket:
        # Test text
        messages = [
            {"text": "Hello, I am calling from your bank."},
        ]

        for msg in messages:
            print(f"Sending text: {msg['text']}")
            await websocket.send(json.dumps(msg))
            response = await websocket.recv()
            print(f"Received: {response}")

        # Test binary (mocked STT)
        audio_msg = "Please provide your OTP immediately.".encode('utf-8')
        print(f"Sending binary: {audio_msg}")
        await websocket.send(audio_msg)
        response = await websocket.recv()
        print(f"Received: {response}")

if __name__ == "__main__":
    try:
        asyncio.run(test_websocket())
    except Exception as e:
        print(f"Error: {e}")
