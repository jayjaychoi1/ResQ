import base64

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class VoiceConsumer(AsyncWebsocketConsumer):
    """
    consumes raw voice data in JSON form receives from Twilio server
    """
    async def connect(self):
        print("call begins")
        await self.accept()

    async def disconnect(self, close_code):
        print("call ends")
        pass

    async def receive(self, text_data):
        """
        receives raw voice data in JSON form, decode it with base 64, and save it as mp3 file. The name of file is "streamSid_sequenceNumber.mp3"
        sequence_number = order of raw voice data
        stream_sid = Unique Twilio stream id
        """
        data = json.loads(text_data)
        sequence_number = data['sequenceNumber']
        stream_sid = data['streamSid']
        payload_base64 = data['media']['payload']
        payload_decoded = base64.b64decode(payload_base64)
        with open(stream_sid + "_" + sequence_number + ".mp3", "wb") as audio_file:
            audio_file.write(payload_decoded)


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
        data = event["message"]
        await self.send(text_data=json.dumps(data))

class TranslateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['raw_sentence']
        # call translator function