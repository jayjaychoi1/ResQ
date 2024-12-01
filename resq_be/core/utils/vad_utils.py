import wave
import webrtcvad


def is_speech_in_audio(file_path):
    """
    Detects whether the audio file contains speech using WebRTC VAD.

    Args:
        file_path (str): Path to the audio file.

    Returns:
        bool: True if speech is detected, False otherwise.
    """
    vad = webrtcvad.Vad()
    vad.set_mode(3)  # Aggressive mode for detecting speech

    with wave.open(file_path, "rb") as wf:
        # Ensure the audio is in the correct format
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            raise ValueError("Audio must be 16kHz, mono, and 16-bit PCM.")
        
        frames = wf.readframes(wf.getnframes())
        return vad.is_speech(frames[:640], wf.getframerate())
