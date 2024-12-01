import base64
# import websocket
# import websockets
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from rest_framework.response import Response
from resq_be.core.utils.chat_utils import send
# added for vad and stt part
from .utils.vad_utils import is_speech_in_audio
from .utils.stt_utils import transcribe_audio
import os

class VoiceConsumer(AsyncWebsocketConsumer):
    """
    consumes raw voice data in JSON form receives from Twilio server
    and call VAD -> STT -> AI -> CHAT
    """

    async def connect(self):
        print("websocket connected")
        await self.accept()

    async def disconnect(self, close_code):
        print("websocket ends")
        pass

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
            payload_decoded = base64.b64decode(payload_base64)
            print("[", speaker_id, "-", sequence_number, "]: ", payload_decoded)

            # Save audio as raw file
            file_path = f"uploaded_audio/{data['streamSid']}_{sequence_number}.raw"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as audio_file:
                audio_file.write(payload_decoded)

            # Perform VAD
            if is_speech_in_audio(file_path):
                # Perform STT if speech is detected
                try:
                    transcription = transcribe_audio(file_path)
                    print("Transcription:", transcription)
                    # Optionally, send transcription to the frontend
                    await self.send(json.dumps({"transcription": transcription}))
                except Exception as e:
                    print("Error in STT:", str(e))
                    await self.send(json.dumps({"error": str(e)}))
            else:
                print("No speech detected in audio.")
                await self.send(json.dumps({"error": "No speech detected."}))

        elif event_type == "connected":
            print("Stream connected")

        elif event_type == "start":
            print("Stream begins")
            print("call_sid: ", data['start'].get('callSid'))
            print("stream_sid: ", data["streamSid"])

        elif event_type == "stop":
            print("Stream ends")
            print("call_sid: ", data['stop'].get('callSid'))
            print("stream_sid: ", data["streamSid"])

        else:
            print("Unknown event type:", event_type)


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
                "user": user_id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
