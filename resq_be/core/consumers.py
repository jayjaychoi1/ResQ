import asyncio
import base64
import sys

from channels.generic.websocket import AsyncWebsocketConsumer
import json
import requests

sys.path.append("C:\\Users\\user\\PycharmProjects\\ResQ\\.venv\\Lib\\site-packages")
sys.path.append("C:\\Users\\user\\PycharmProjects\\ResQ\\.venv\\Lib\\site-packages\\google")
from google.cloud import speech
from google.oauth2 import service_account
from google.api_core import exceptions as google_exceptions

class VoiceConsumer(AsyncWebsocketConsumer):
    """
    consumes raw voice data in JSON form receives from Twilio server
    and call VAD -> STT -> AI -> CHAT
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_path = "C:\\Users\\user\\PycharmProjects\\ResQ\\resq_be\\core\\utils\\resq-443606-827aa1a8ebca.json"
        self.credentials = service_account.Credentials.from_service_account_file(self.key_path)
        self.client = speech.SpeechClient(credentials=self.credentials)

        # Streaming configuration for Google STT
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MULAW,
            sample_rate_hertz=8000,
            language_code="ko-KR",
            enable_automatic_punctuation=True,
        )
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.config,
            interim_results=True,
        )
        self.audio_queue = asyncio.Queue()  # Queue for audio chunks

    async def connect(self):
        print("websocket connected")
        await self.accept()
        self.stt_task = asyncio.create_task(self.google_stt_stream())

    async def disconnect(self, close_code):
        print("websocket ends")
        self.stt_task.cancel()

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
            await self.audio_queue.put(payload_decoded)

            # print(speaker_id, "-", sequence_number, ": ", payload_decoded)
            # # Send audio to Google STT
            # transcript = await self.transcribe_audio(payload_decoded)
            # if transcript:
            #     # Send transcription back to the WebSocket client
            #     print(transcript)

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

    async def google_stt_stream(self):
        """
        Streams audio from the audio queue to Google STT and processes transcription results.
        """
        # Generator to create streaming requests
        async def request_generator():
            while True:
                chunk = await self.audio_queue.get()
                if chunk is None:  # End of stream signal
                    break
                yield speech.StreamingRecognizeRequest(audio_content=chunk)

        try:
            # Send streaming requests to Google STT
            responses = self.client.streaming_recognize(
                config=self.streaming_config,
                requests=request_generator(),
            )

            # Process responses
            async for response in responses:
                for result in response.results:
                    if result.is_final:
                        transcript = result.alternatives[0].transcript
                        print("Transcript:", transcript)


        except Exception as e:
            print(f"Error during Google STT streaming: {e}")

    # async def transcribe_audio(self, audio_chunk):
    #     """
    #     Send audio chunk to Google Cloud Speech-to-Text API for transcription asynchronously.
    #     """
    #     config = speech.RecognitionConfig(
    #         encoding=speech.RecognitionConfig.AudioEncoding.MULAW,
    #         sample_rate_hertz=8000,
    #         language_code="ko-KR",
    #         enable_automatic_punctuation=True,
    #     )
    #     audio = speech.RecognitionAudio(content=audio_chunk)
    #
    #     try:
    #         loop = asyncio.get_event_loop()
    #         response = await loop.run_in_executor(None, self.client.recognize, config, audio)
    #         if response.results:
    #             return response.results[0].alternatives[0].transcript
    #     except google_exceptions.GoogleAPICallError as e:
    #         print(f"Error transcribing audio: {e}")
    #         return None

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
