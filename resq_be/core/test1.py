import base64
import json
import pygame
from flask import Flask, request
from flask_sock import Sock, ConnectionClosed
from twilio.twiml.voice_response import VoiceResponse, Start
from twilio.rest import Client
from pydub import AudioSegment
from pydub.playback import play
import io

app = Flask(__name__)
sock = Sock(app)
twilio_client = Client()


@app.route('/call', methods=['POST'])
def call():
    """Accept a phone call."""
    response = VoiceResponse()
    start = Start()
    start.stream(url=f'wss://{request.host}/stream')
    response.append(start)
    response.say('Please leave a message')
    response.pause(length=60)
    print(f'Incoming call from {request.form["From"]}')
    return str(response), 200, {'Content-Type': 'text/xml'}


@sock.route('/stream')
def stream(ws):
    """Receive and transcribe audio stream."""
    audio_data = b''  # Initialize an empty bytes object to store audio data.

    while True:
        message = ws.receive()
        packet = json.loads(message)

        if packet['event'] == 'start':
            print('Streaming is starting')
        elif packet['event'] == 'media':
            audio_payload = base64.b64decode(packet['media']['payload'])
            audio_data += audio_payload
            # Play the audio live using pygame
            print(packet['media']['payload'])
            play_audio_live(audio_payload)
        elif packet['event'] == 'stop':
            print('\nStreaming has stopped')

            if audio_data:
                # Save the audio as an MP3 file
                save_audio_as_mp3(audio_data, "audio.mp3")
                print("Audio saved as audio.mp3")
            else:
                print("No audio data received")
            break


def play_audio_live(audio_payload):
    """Play audio live using pygame."""
    pygame.mixer.init()
    audio_chunk = pygame.mixer.Sound(buffer=audio_payload)
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=1)

    pygame.init()
    beep = pygame.mixer.Sound(buffer=audio_payload)
    pygame.mixer.Sound.play(audio_chunk)
data_bytes = b"".join(data)
wave_write = pywav.WavWrite(name, 2, 8000,2,7)

def save_audio_as_mp3(audio_data, mp3_filename):
    """Save audio data as an MP3 file."""
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=1)
    pygame.init()
    beep = pygame.mixer.Sound(buffer=audio_data)

    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
    audio_segment.export(mp3_filename, format='mp3')
    with open(mp3_filename, 'wb') as mp3_file:

