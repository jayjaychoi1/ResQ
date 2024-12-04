import asyncio
import audioop
import base64
import sys
import wave

from channels.generic.websocket import AsyncWebsocketConsumer
import json
sys.path.append("C:\\Users\\user\\PycharmProjects\\ResQ\\.venv\\Lib\\site-packages\\pywav")
sys.path.append("C:\\Users\\user\\PycharmProjects\\ResQ\\.venv\\Lib\\site-packages\\")
import pywav

#from openai import OpenAI
# def call_whisper(audio_file):
#     client = OpenAI(api_key = "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")
#     audio_file= open(audio_file, "rb")
#     transcription = client.audio.transcriptions.create(
#       model="whisper-1",
#       file=audio_file
#     )
#     print(transcription.text)

class VoiceConsumer(AsyncWebsocketConsumer):
    """
    consumes raw voice data in JSON form receives from Twilio server
    and call VAD -> STT -> AI -> CHAT
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_queue = asyncio.Queue()  # 비동기 버퍼
        self.flag = "OFF"

    async def connect(self):
        print("websocket connected")
        await self.accept()

    async def disconnect(self, close_code):
        print("websocket ends")

    async def receive(self, text_data):
        """
        receives raw voice data in JSON form, decode it with base 64, and save it as mp3 file. The name of file is "streamSid_sequenceNumber.mp3"
        sequence_number = order of raw voice data
        stream_sid = Unique Twilio stream id
        """
        data = json.loads(text_data)
        event_type = data.get("event")

        if event_type == "media":
            # sequence of raw voice data
            sequence_number = data['sequenceNumber']
            payload_base64 = data['media']['payload']
            # speaker 1: inbound(caller), speaker 2: outbound(callee)
            speaker_id = data['media']['track']
            if speaker_id == 'inbound':
                payload_decoded = base64.b64decode(payload_base64)
                await self.audio_queue.put(payload_decoded)

        elif event_type == "connected":
            print("Stream connected")

        elif event_type == "start":
            print("Stream begins")
            print("call_sid: ", data['start'].get('callSid'))
            print("stream_sid: ", data["streamSid"])

        elif event_type == "stop":
            print("Stream ends")
            audio_data = b""

            while not self.audio_queue.empty():
                audio_data += await self.audio_queue.get()

            pcm_data = audioop.ulaw2lin(audio_data, 2)

            # WAV 파일 생성
            with wave.open("Recording.wav", "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(8000)  # 8000 Hz
                wav_file.writeframes(pcm_data)

        else:
            print("Unknown event type:", event_type)

    async def toggle_flag(self, event):
        self.flag = event['flag']



class ChatConsumer(AsyncWebsocketConsumer):
    """
    accept websocket connect/disconnect request and make a group-chat room, receive message from user client and broadcast it to group-chat room.
    """
    async def connect(self):
        print("chat begins")
        await self.channel_layer.group_add("chat", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print("chat ends")
        await self.channel_layer.group_discard("chat", self.channel_name)
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_id = data['user_id']
        message = data['message']
        await self.channel_layer.group_send(
            "chat",
            {
                "type": "chat_message",
                "message": message,
                "user_id": user_id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

# class AIConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data.get("message", "")
#
#         await
#
#     async def send_translate(self, event, text_data):
#         data = json.loads(text_data)
#         message = data.get("message", "")
#
#         uri = "ws://server-b.example.com/ws/endpoint/"
#         async with websockets.connect(uri) as websocket:
#             await websocket.send(json.dumps({"message": message}))
#             response = await websocket.recv()
#
#         await self.send(text_data=json.dumps({"status": f"Message sent to server B: {response}"}))