import base64
import json
import wave
import numpy as np
from pydub import AudioSegment
from channels.generic.websocket import AsyncWebsocketConsumer
import webrtcvad
from vosk import Model, KaldiRecognizer
import aiohttp


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
        print("WebSocket connection established.")
        await self.accept()

    async def disconnect(self, close_code):

        print("WebSocket disconnected.")

    async def receive(self, text_data):
   """
        receives raw voice data in JSON form, decode it with base 64, and save it as mp3 file. The name of file is "streamSid_sequenceNumber.mp3"
        sequence_number = order of raw voice data
        stream_sid = Unique Twilio stream id
        """
        try:
            data = json.loads(text_data)
            sequence_number = data.get("sequenceNumber")
            stream_sid = data.get("streamSid")
            payload_base64 = data["media"]["payload"] 
            payload_decoded = base64.b64decode(payload_base64)
            audio_file_name = f"{stream_sid}_{sequence_number}.mp3"
            with open(audio_file_name, "wb") as audio_file:
                audio_file.write(payload_decoded)

            # Converting the MP3 file to PCM WAV format
            pcm_audio_path = self.convert_to_pcm(audio_file_name)

            # Performing Voice Activity Detection (VAD)
            if self.vad_algorithm(pcm_audio_path):
                print("Speech detected. Proceeding to STT...")

                # Performing Speech-to-Text (STT) using VOSK
                transcription = self.transcribe_audio_with_vosk(pcm_audio_path)
                print(f"Transcription: {transcription}")

                # Calling the AI service with the transcription
                ai_response = await self.call_ai(transcription)

                # Broadcasting the transcription and AI response
                await self.broadcast_chat_message(transcription, ai_response)
            else:
                print("No speech detected.")
        except Exception as e:
            print(f"Error processing audio: {e}")

    def convert_to_pcm(self, audio_path):
        """
        Converts an audio file (MP3/WAV) to PCM format (16-bit mono, 16kHz).

        Args:
            audio_path (str): Path to the input audio file.

        Returns:
            str: Path to the converted PCM WAV file.
        """
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        pcm_path = audio_path.replace(".mp3", "_pcm.wav")
        audio.export(pcm_path, format="wav")
        return pcm_path

    def vad_algorithm(self, pcm_path):
        """
        Performs Voice Activity Detection (VAD) on an audio file.

        Args:
            pcm_path (str): Path to the PCM WAV file.

        Returns:
            bool: True if speech is detected, False otherwise.
        """
        vad = webrtcvad.Vad(3)
        with wave.open(pcm_path, "rb") as wf:
            sample_rate = wf.getframerate()
            frame_duration_ms = 20
            n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
            audio = wf.readframes(wf.getnframes())

           
            for i in range(0, len(audio), n):
                frame = audio[i:i + n]
                if len(frame) < n:
                    continue  
                if vad.is_speech(frame, sample_rate):
                    return True
        return False

    def transcribe_audio_with_vosk(self, pcm_path):
        """
        Transcribes audio to text using the VOSK Speech-to-Text (STT) library.

        Args:
            pcm_path (str): Path to the PCM WAV file.

        Returns:
            str: Transcription of the audio.
        """
        vosk_model_path = "models/vosk.blabla"  # Write VOSK model path, after installing it 
        model = Model(vosk_model_path)
        recognizer = KaldiRecognizer(model, 16000)

        with wave.open(pcm_path, "rb") as wf:
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    results.append(json.loads(recognizer.Result()))

            # Finalize transcription
            final_result = json.loads(recognizer.FinalResult())
            results.append(final_result)

        # Combine all results into a single transcription string
        transcription = " ".join([res.get("text", "") for res in results])
        return transcription

    async def call_ai(self, transcription):
        """
        Sends the transcription to an AI service and processes the response.

        Args:
            transcription (str): The input text to be processed by the AI.

        Returns:
            str: The AI's response to the input transcription.
            Iuliya check here pls..
        """
        print("AI processing transcription...")

        # Example API endpoint and headers
        ai_service_url = "https://api.example-ai-service.com/process"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_API_KEY",  # Replace with your actual API key
        }

      
        payload = {
            "input_text": transcription,
            "context": "Emergency response AI model.",  
        }

        try:
            # Send a POST request to the AI service
            async with aiohttp.ClientSession() as session:
                async with session.post(ai_service_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        # Parse the response JSON
                        data = await response.json()
                        ai_response = data.get("response", "No response received.")
                        print(f"AI response: {ai_response}")
                        return ai_response
                    else:
                        # Handle non-200 status codes
                        error_message = await response.text()
                        print(f"Error from AI service: {response.status} - {error_message}")
                        return f"AI service error: {response.status}"
        except Exception as e:
            # Handle any exceptions during the request
            print(f"Error communicating with AI service: {e}")
            return "Error communicating with AI service."

    async def broadcast_chat_message(self, transcription, ai_response):
        """
        Broadcasts transcription and AI response to a WebSocket group.

        Args:
            transcription (str): The transcribed text from STT.
            ai_response (str): The AI's response to the transcription.
        """
        user_id = "system"  # Replace with actual user ID if needed
        await self.channel_layer.group_send(
            "chat",
            {
                "type": "chat_message",
                "message": ai_response,
                "user": user_id,
            }
        )


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Accepts WebSocket connect/disconnect requests and manages a group chat room.
    """

    async def connect(self):
        print("Chat WebSocket connection established.")
        await self.channel_layer.group_add("chat", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print("Chat WebSocket disconnected.")
        await self.channel_layer.group_discard("chat", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_id = data.get("user_id", "anonymous")
        message = data.get("message", "")
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
