from dotenv import load_dotenv
from openai_tool import recipe_generator
import pyaudio
import asyncio
import websockets
import json
import base64
import os

load_dotenv()
assemblyai_client = os.getenv("ASSEMBLYAI_KEY")


fpb = 3200
format = pyaudio.paInt16
channels = 1
rate = 16000

p = pyaudio.PyAudio()

stream = p.open(
    format=format,
    channels=channels,
    rate=rate,
    input=True,
    frames_per_buffer=fpb
)

URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"


async def send_recieve():
    async with websockets.connect(
        URL,
        ping_timeout=20,
        ping_interval=5,
        extra_headers={"Authorization": assemblyai_client}
    ) as _ws:
        await asyncio.sleep(0.1)
        session_begins = await _ws.recv()
        print(session_begins)
        print("Starting interactive recipe chat with ChatGPT. Say exit to end the session.")

        async def send():
            while True:
                try:
                    data = stream.read(fpb, exception_on_overflow=False)
                    data = base64.b64encode(data).decode("utf-8")
                    json_data = json.dumps({"audio_data": data})
                    await _ws.send(json_data)

                    if "exit" in json_data:
                        break

                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.encode == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"
                await asyncio.sleep(0.01)

        async def recieve():
            while True:
                try:
                    result_str = await _ws.recv()
                    result = json.loads(result_str)
                    prompt = result["text"]

                    if "exit" in prompt:
                        break

                    if prompt and result["message_type"] == "FinalTranscript":
                        print("Me: ", prompt)
                        response = recipe_generator(prompt)
                        print("OpenAI:", response)
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.encode == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"
                await asyncio.sleep(0.01)

        send_result, receive_result = await asyncio.gather(send(), recieve())

asyncio.run(send_recieve())
