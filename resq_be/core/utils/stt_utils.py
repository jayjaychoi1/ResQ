# import os
# import wave
# import json
# from vosk import Model, KaldiRecognizer
#
#
# def transcribe_audio_vosk(filepath, model_path='models/vosk-model-small-en-us-0.22'):
#     """Transcribes audio using Vosk."""
#     if not os.path.exists(model_path):
#         raise FileNotFoundError(f"Model not found at {model_path}")
#
#     # Load Vosk model
#     model = Model(model_path)
#     recognizer = KaldiRecognizer(model, 16000)
#
#     with wave.open(filepath, "rb") as wf:
#         if wf.getnchannels() != 1:
#             raise ValueError("Audio file must be mono for Vosk")
#         if wf.getframerate() != 16000:
#             raise ValueError("Audio sample rate must be 16kHz for Vosk")
#
#         transcription = ""
#         while True:
#             data = wf.readframes(4000)
#             if len(data) == 0:
#                 break
#             if recognizer.AcceptWaveform(data):
#                 result = json.loads(recognizer.Result())
#                 transcription += result.get("text", "") + " "
#
#         # Get final partial results
#         final_result = json.loads(recognizer.FinalResult())
#         transcription += final_result.get("text", "")
#
#     return transcription.strip()

# def transcribe_audio_with_vosk(audio_path, model_path='models/vosk-model-small-en-us-0.22'):
#     """transcribes PCM audio to text using Vosk"""
#     if not os.path.exists(model_path):
#         raise FileNotFoundError(f"Model not found at {model_path}")
#
#     model = Model(model_path)
#     recognizer = KaldiRecognizer(model, 16000)
#
#     with wave.open(audio_path, "rb") as wf:
#         transcription = ""
#         while True:
#             data = wf.readframes(4000)
#             if len(data) == 0:
#                 break
#             if recognizer.AcceptWaveform(data):
#                 result = json.loads(recognizer.Result())
#                 transcription += result.get("text", "") + " "
#
#         final_result = json.loads(recognizer.FinalResult())
#         transcription += final_result.get("text", "")
#
#     return transcription.strip()

# def stt(pcm_audio_path):
#     # transcription = transcribe_audio_with_vosk(pcm_audio_path)
#     return transcription
