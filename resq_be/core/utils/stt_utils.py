import wave
from vosk import Model, KaldiRecognizer

VOSK_MODEL_PATH = "/Users/soulen/Desktop/dec/ResQ/models/vosk-model-small-en-us-0.15"


# Load the Vosk model (ensure the model exists at the specified path)
vosk_model = Model(VOSK_MODEL_PATH)


def transcribe_audio(file_path):
    """
    Transcribes the given audio file using Vosk STT.

    Args:
        file_path (str): Path to the audio file.

    Returns:
        str: The transcribed text.
    """
    recognizer = KaldiRecognizer(vosk_model, 16000)
    transcription = ""

    with wave.open(file_path, "rb") as wf:
        # Ensure the audio is in the correct format
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            raise ValueError("Audio must be 16kHz, mono, and 16-bit PCM.")
        
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                transcription += result
    return transcription
