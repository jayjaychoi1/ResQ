import asyncio
import audioop
import base64
import sys
import wave
from datetime import datetime

sys.path.append("C:\\Users\\user\\PycharmProjects\\ResQ\\.venv\\Lib\\site-packages\\websockets")
sys.path.append("C:\\Users\\user\\PycharmProjects\\ResQ\\.venv\\Lib\\site-packages\\")
import websockets
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from channels.layers import get_channel_layer
from openai import OpenAI


class VoiceConsumer(AsyncWebsocketConsumer):
    """
    consumes raw voice data in JSON form receives from Twilio server
    and call VAD -> STT -> AI -> CHAT
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inbound_audio_queue = asyncio.Queue()  # 비동기 버퍼
        self.outbound_audio_queue = asyncio.Queue()  # 비동기 버퍼
        self.inbound_flag = "off"
        self.outbound_flag = "off"
        self.inbound_idx = 0
        self.outbound_idx = 0
        self.external_ws = None
        self.external_ws_url = "wss://c1ba-211-179-53-26.ngrok-free.app/ws/some_path/"
        self.max_size = 250
        self.tmp = 0

    async def connect(self):
        print("websocket connected")
        self.external_ws = await websockets.connect(self.external_ws_url)
        print("external websocket connected")
        await self.accept()

    async def disconnect(self, close_code):
        await self.external_ws.close()
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

            # if speaker_id == 'inbound' and self.inbound_flag == "on":
            #     payload_decoded = base64.b64decode(payload_base64)
            #     await self.inbound_audio_queue.put(payload_decoded)
            #
            # elif speaker_id == 'outbound' and self.outbound_flag == "on":
            #     payload_decoded = base64.b64decode(payload_base64)
            #     await self.outbound_audio_queue.put(payload_decoded)
            if speaker_id == 'inbound':
                payload_decoded = base64.b64decode(payload_base64)
                await self.inbound_audio_queue.put(payload_decoded)

                if self.inbound_audio_queue.qsize() > self.max_size:
                    if self.tmp == 1:
                        self.tmp = 0
                        audio_data = b""
                        while not self.inbound_audio_queue.empty():
                            audio_data += await self.inbound_audio_queue.get()
                        print("no_inbound_audio")

                        if audio_data:
                            pcm_data = audioop.ulaw2lin(audio_data, 2)

                            with wave.open("inbound.wav", "wb") as wav_file:
                                wav_file.setnchannels(1)  # Mono
                                wav_file.setsampwidth(2)  # 16-bit
                                wav_file.setframerate(8000)  # 8000 Hz
                                wav_file.writeframes(pcm_data)

                            translated_sentences = await self.call_translate(await self.call_whisper("inbound.wav"))
                            translated_dict = {
                                "user_id": "inbound",
                                "message": translated_sentences
                            }
                            translated_json = json.dumps(translated_dict)
                            await self.chat_message(translated_json)
                    else:
                        self.tmp = 1
                        while not self.inbound_audio_queue.empty():
                            await self.inbound_audio_queue.get()
                        print("go_inbound_audio")


        elif event_type == "connected":
            print("Stream connected")

        elif event_type == "start":
            print("Stream begins")
            print("call_sid: ", data['start'].get('callSid'))
            print("stream_sid: ", data["streamSid"])

        elif event_type == "stop":
            print("Stream ends")

        else:
            print("Unknown event type:", event_type)

    async def call_translate(self, untranslated_text):
        untranslated_json = {
            "message": untranslated_text
        }
        json_message = json.dumps(untranslated_json)
        await self.external_ws.send(json_message)

        response = await self.external_ws.recv()
        result = json.loads(response)
        print(result['message'])
        return result["message"]

    async def toggle_flag(self, event):
        channel = event['channel']
        flag = event['flag']

        if channel == "inbound" and flag == "on":
            print("on")
            self.inbound_flag = "on"

        elif channel == "inbound" and flag == "off":
            print("off")
            self.inbound_flag = "off"

        elif channel == "outbound" and flag == "on":
            self.outbound_flag = "on"

        elif channel == "outbound" and flag == "off":
            self.outbound_flag = "off"
            audio_data = b""
            while not self.outbound_audio_queue.empty():
                audio_data += await self.outbound_audio_queue.get()

            pcm_data = audioop.ulaw2lin(audio_data, 2)

            with wave.open("outbound.wav", "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(8000)  # 8000 Hz
                wav_file.writeframes(pcm_data)

            translated_sentences = await self.call_translate(await self.call_whisper("outbound.wav"))
            translated_dict = {
                "user_id": "outbound",
                "message": translated_sentences
            }
            translated_json = json.dumps(translated_dict)
            await self.chat_message(translated_json)

    async def call_whisper(self, audio_file_path):
        client = OpenAI(
            api_key="")
        audio_file = open(audio_file_path, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language = "en"
        )

        return transcription.text

    async def chat_message(self, text_data):
        channel_layer = get_channel_layer()
        data = json.loads(text_data)
        user_id = data['user_id']
        message = data['message']
        channel_layer.group_send(
            "chat",
            {
                "type": "chat_message",
                "message": message,
                "user_id": user_id,
            }
        )





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


# class TestConsumer(AsyncWebsocketConsumer):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.external_ws = None
#         self.external_ws_url = "wss://c1ba-211-179-53-26.ngrok-free.app/ws/some_path/"
#
#     async def connect(self):
#         self.external_ws = await websockets.connect(self.external_ws_url)
#         print("Connected to external WebSocket server")
#         await self.accept()
#
#     async def receive(self, text_data):
#         to_send = json.loads(text_data)
#         untranslated_json = {
#             "user_id": to_send['user_id'],
#             "message": to_send['message']
#         }
#         json_message = json.dumps(untranslated_json)
#         await self.external_ws.send(json_message)
#         response = await self.external_ws.recv()
#         await self.send(response)
