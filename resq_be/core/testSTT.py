# import wave
# import openai
# audio_file_path = "utils/testv.wav"
#
# def binary_to_wav(binary_data, output_path, params):
#     """
#     Converts binary audio data back to a WAV file.
#
#     Args:
#         binary_data (bytes): Binary audio data.
#         output_path (str): Path to save the WAV file.
#         params (tuple): Tuple of WAV file parameters (nchannels, sampwidth, framerate, nframes).
#     """
#     with wave.open(output_path, 'wb') as wav_file:
#         # Set the WAV file parameters
#         nchannels, sampwidth, framerate = params
#         wav_file.setnchannels(nchannels)
#         wav_file.setsampwidth(sampwidth)
#         wav_file.setframerate(framerate)
#         # Write the binary audio data as frames
#         wav_file.writeframes(binary_data)
#
# params = (1, 2, 44100)  # Mono, 16-bit samples, 16 kHz sample rate
# output_wav_path = "output.wav"
# binary_data = wav_to_binary(audio_file_path)
# binary_to_wav(binary_data, output_wav_path, params)
#
# print(get_wav_params(audio_file_path))
# from openai import OpenAI
# client = OpenAI(api_key = "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")
#
# audio_file= open("output.wav", "rb")
# transcription = client.audio.transcriptions.create(
#   model="whisper-1",
#   file=audio_file
# )
# print(transcription.text)
