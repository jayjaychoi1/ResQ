import base64
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class VoiceConsumer(AsyncWebsocketConsumer):
    """
    consumes raw voice data in JSON form receives from Twilio server
    and call VAD -> STT -> AI -> CHAT
    """
    """
    CALL AI CODE 1
    async def ai_translate(self, server_url, message):
        async with websockets.connect(server_url) as websocket:
            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            return json.loads(response)
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
        """
        check if audio stacks enough
        """

        """
        CALL VAD CODE
        """

        """
        CALL STT CODE
        """

        """
        CALL AI CODE 2
        server_url = "ws://127.0.0.1:9000/ws/as_routing.py_in_Junia's/"
        result = await self.connect_to_other_server(server_url, {"message": after_STT})
        !!! u must decode result with unicode !!!
        !!! u must fix url as Junia's routing.py !!!
        """

        """
        CALL CHAT CODE
        - user_id = id of sender
        - result = translated result

        channel_layer = get_channel_layer() 
        async_to_sync(channel_layer.group_send)(
        "chat",
            {
                "type": "chat_message",  
                "message": result,
                "user": user_id,
            }
        )
        """



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
