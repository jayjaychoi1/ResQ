import asyncio
import audioop
import base64
import sys
import wave
import webrtcvad

from resq_be.core.config import conf_TRANSLATE_SERVER_URL, conf_CHAT_SERVER_URL, conf_API_KEY, conf_LIB_PATH

sys.path.append(conf_LIB_PATH + "websockets")
sys.path.append(conf_LIB_PATH)
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from openai import OpenAI

class VoiceConsumer(AsyncWebsocketConsumer):
    """
    consumes raw voice data in JSON form receives from Twilio server
    and call VAD -> STT -> AI -> CHAT
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_queue = {
            "inbound": asyncio.Queue(),
            "outbound": asyncio.Queue(),
        }
        self.speech_cnt = {
            "inbound": 0,
            "outbound": 0,
        }
        self.silent_cnt = {
            "inbound": 0,
            "outbound": 0,
        }
        self.USER_ID = {"inbound", "outbound"}
        self.chat_server = None
        self.translate_server = None
        self.chat_server_url = conf_CHAT_SERVER_URL
        self.translate_server_url = conf_TRANSLATE_SERVER_URL
        self.vad = webrtcvad.Vad(3)
        self.MAX_SILENT = 15
        self.MIN_SPEECH = 15
        self.CHANNEL = 1
        self.SAMP_WIDTH = 2
        self.SAMP_RATE = 8000


    async def connect(self):
        print("websocket connected")
        await self.channel_layer.group_add("chat", self.channel_name)
        self.translate_server = await websockets.connect(self.translate_server_url)
        self.chat_server = await websockets.connect(self.chat_server_url)
        await self.accept()

    async def disconnect(self, close_code):
        await self.translate_server.close()
        await self.chat_server.close()
        await self.channel_layer.group_discard("chat", self.channel_name)
        print("websocket ends")

    async def receive(self, rcv_json):
        """
        receives raw voice data in JSON form, decode it with base 64, and save it as mp3 file. The name of file is "streamSid_sequenceNumber.mp3"
        sequence_number = order of raw voice data
        stream_sid = Unique Twilio stream id
        """
        rcv_dict = json.loads(rcv_json)
        event_type = rcv_dict.get("event")

        if event_type == "media":
            # sequence of raw voice data
            sequence_number = rcv_dict['sequenceNumber']
            payload_base64 = rcv_dict['media']['payload']
            # speaker 1: inbound(caller), speaker 2: outbound(callee)
            user_id = rcv_dict['media']['track']

            """
            is_speech?
            you don't have to worry about its real speech -> cleaned by next module
            """
            payload_decoded = base64.b64decode((payload_base64))
            if self.vad.is_speech(payload_decoded, sample_rate=8000):
                self.speech_cnt[user_id] += 1
                self.audio_queue[user_id].put_nowait(payload_decoded)

            else:
                self.silent_cnt[user_id] += 1

            """
            enough silent detected -> process it
            """
            for user_id in self.USER_ID:
                if self.silent_cnt[user_id] > self.MAX_SILENT:
                    self.speech_cnt[user_id] = 0
                    if len(self.audio_queue[user_id]) > self.MIN_SPEECH:
                        audio_data = b""
                        while not self.audio_queue[user_id].empty():
                            audio_data += self.audio_queue[user_id].get()
                        pcm_data = audioop.ulaw2lin(audio_data, 2)
                        with wave.open(user_id + ".wav", "wb") as chunk_file:
                            chunk_file.setnchannels(self.CHANNEL),  # Mono
                            chunk_file.setsampwidth(self.SAMP_WIDTH)  # 16-bit
                            chunk_file.setframerate(self.SAMP_RATE)  # 8000 Hz
                            chunk_file.writeframes(pcm_data)
                        translated_sentence = await self.call_translate(await self.call_stt(user_id + ".wav", user_id), user_id)
                        dict_data = {
                            'user_id': user_id,
                            'message': translated_sentence,
                            'translated': 'yes'
                        }
                        json_data = json.dumps(dict_data)
                        await self.send_translated_chat(json_data)

                    else:
                        """
                        but not enough speech accumulated -> clean queue
                        """
                        while not self.audio_queue[user_id].empty():
                            self.audio_queue[user_id].get()

        elif event_type == "connected":
            print("Stream connected")

        elif event_type == "start":
            print("Stream begins")
            print("call_sid: ", rcv_dict['start'].get('callSid'))
            print("stream_sid: ", rcv_dict["streamSid"])

        elif event_type == "stop":
            print("Stream ends")

        else:
            print("Unknown event type:", event_type)

    async def call_translate(self, untranslated_text, user_id):
        dict_data = {
            'user_id': user_id,
            'message': untranslated_text
        }
        json_data = json.dumps(dict_data)
        await self.translate_server.send(json_data)

        rcv_json = await self.translate_server.recv()
        rcv_dict = json.loads(rcv_json)
        return rcv_dict['message']

    async def call_stt(self, audio_file_path, user_id):
        lang = 'en' if user_id == 'inbound' else 'ko'
        client = OpenAI(api_key=conf_API_KEY)
        audio_file = open(audio_file_path, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language = lang
        )
        return transcription.text

    async def send_translated_chat(self, rcv_json):
        rcv_dict = json.loads(rcv_json)
        user_id = rcv_dict['user_id']
        message = rcv_dict['message']
        translated = rcv_dict['translated']
        dict_data = {
            'user_id': user_id,
            'message': message,
            'translated': translated,
            'media_type': 'voice'
        }
        json_data = json.dumps(dict_data)
        await self.chat_server.send(json_data)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    accept websocket connect/disconnect request and make a group-chat room, receive message from user client and broadcast it to group-chat room.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translate_server = None
        self.translate_server_url = conf_TRANSLATE_SERVER_URL

    async def connect(self):
        print("chat begins")
        await self.channel_layer.group_add("chat", self.channel_name)
        self.translate_server = await websockets.connect(self.translate_server_url)
        await self.accept()

    async def disconnect(self, close_code):
        print("chat ends")
        self.translate_server.close()
        await self.channel_layer.group_discard("chat", self.channel_name)
        pass

    async def receive(self, rcv_json):
        rcv_dict = json.loads(rcv_json)
        media_type = rcv_dict['media_type']
        user_id = rcv_dict['user_id']
        message = rcv_dict['message']

        if media_type == 'voice':
            translated_message = message
            await self.channel_layer.group_send(
                'chat',
                {
                    'type': 'chat_message',
                    'message': translated_message,
                    'user_id': user_id,
                    'translated': 'yes'
                }
            )

        else:
            await self.channel_layer.group_send(
                'chat',
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': user_id,
                    'translated': 'no'
                }
            )

            translated_message = await self.call_translate(message, user_id)
            await self.channel_layer.group_send(
                'chat',
                {
                    'type': 'chat_message',
                    'message': translated_message,
                    'user_id': user_id,
                    'translated': 'no'
                }
            )

    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']
        translated = event['translated']
        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id,
            'translated': translated
        }))

    async def call_translate(self, untranslated_text, user_id):
        dict_data = {
            'user_id': user_id,
            'message': untranslated_text
        }
        json_data = json.dumps(dict_data)
        await self.translate_server.send(json_data)

        rcv_json = await self.translate_server.recv()
        rcv_dict = json.loads(rcv_json)
        return rcv_dict['message']

    async def call_stt(self, audio_file_path, user_id):
        lang = 'en' if user_id == 'inbound' else 'ko'
        client = OpenAI(api_key=conf_API_KEY)
        audio_file = open(audio_file_path, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language = lang
        )
        return transcription.text