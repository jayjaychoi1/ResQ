import audioop
import wave

import pywav


def twilio_raw_to_wav(raw_binary_data, output_path="final.wav"):
    """
    Converts Twilio Media Stream raw binary data (MULAW) to a WAV file with PCM encoding.

    Args:
        raw_binary_data (bytes): Twilio Media Stream raw binary data in MULAW format.
        output_path (str): Path to save the output WAV file.
    """
    try:
        # Convert MULAW to PCM (16-bit samples)
        pcm_data = audioop.ulaw2lin(raw_binary_data, 2)

        # Write PCM data to a WAV file
        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono channel
            wav_file.setsampwidth(2)  # 16-bit samples (2 bytes)
            wav_file.setframerate(8000)  # 8000 Hz sampling rate
            wav_file.writeframes(pcm_data)

        print(f"WAV file successfully written to {output_path}")
    except Exception as e:
        print(f"Error while converting raw binary data to WAV: {e}")


with open("combined_raw_data.raw", "rb") as raw_file:
    raw_binary_data = raw_file.read()
wave_write = pywav.WavWrite("Recording.wav", 1,8000,8,7)  # 1 stands for mono channel, 8000 sample rate, 8 bit, 7 stands for MULAW encoding
wave_write.write(raw_binary_data)
wave_write.close()
