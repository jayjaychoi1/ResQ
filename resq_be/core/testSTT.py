import asyncio
import base64
import sys
import wave

from google.oauth2 import service_account

sys.path.append("C:\\Users\\user\\PycharmProjects\\ResQ\\.venv\\Lib\\site-packages")
sys.path.append("C:\\Users\\user\\PycharmProjects\\ResQ\\.venv\\Lib\\site-packages\\google")
from google.cloud import speech


def transcribe_file(file_path) -> speech.RecognizeResponse:
    """Transcribe the given audio file.
    Args:
        audio_file (str): Path to the local audio file to be transcribed.
            Example: "resources/audio.wav"
    Returns:
        cloud_speech.RecognizeResponse: The response containing the transcription results
    """
    key_path = "C:\\Users\\user\\PycharmProjects\\ResQ\\resq_be\\core\\utils\\resq-443606-499d2ec4cf97.json"
    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = speech.SpeechClient(credentials=credentials)

    with open(file_path, "rb") as audio_file:
        audio_content = base64.b64encode(audio_file.read()).decode("utf-8")

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="ko-KR",
        sample_rate_hertz=44100,
        enable_automatic_punctuation=True,  # 자동 구두점 추가
    )

    response = client.recognize(config=config, audio=audio)
    print("received")
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response

# def wav_to_raw(wav_file, raw_file):
#     """
#     .wav 파일에서 raw binary data를 추출하여 .raw 파일로 저장합니다.
#
#     Args:
#         wav_file (str): 입력 .wav 파일 경로.
#         raw_file (str): 출력 .raw 파일 경로.
#     """
    # with wave.open(wav_file, "rb") as wav:
    #     # .wav 파일에서 데이터 추출
    #     n_channels = wav.getnchannels()  # 채널 수
    #     sample_width = wav.getsampwidth()  # 샘플 크기 (바이트 단위)
    #     frame_rate = wav.getframerate()  # 샘플링 속도
    #     n_frames = wav.getnframes()  # 총 프레임 수
    #
    #     print(f"Channels: {n_channels}, Sample Width: {sample_width}, Frame Rate: {frame_rate}, Frames: {n_frames}")
    #
    #     # Raw binary data 읽기
    #     raw_data = wav.readframes(n_frames)
    #     with open(raw_file, "wb") as raw:
    #         raw.write(raw_data)
    #     print(raw_data)









# def use_api_request(audio_data):
#     audio_base64 = base64.b64encode(audio_data).decode("utf-8")
#     payload = {
#         "config": {
#             "encoding": "LINEAR16",
#             "sampleRateHertz": 16000,
#             "languageCode": "en-US"
#         },
#         "audio": {
#             "content": audio_base64
#         }
#     }
#     headers = {"Content-Type": "application/json"}
#     start_time = time.time()
#     response = requests.post(endpoint, json=payload, headers=headers)
#     end_time = time.time()
#     return end_time - start_time

async def async_function():
    print("Start")
    await asyncio.sleep(3)  # 비동기 블로킹
    print("End")

asyncio.run(async_function())

# wav_to_raw("utils/testv.wav", "utils/output.raw")
import wave

def get_sample_rate(file_path):
    with wave.open(file_path, "rb") as wav_file:
        return wav_file.getframerate()

file_path = "utils/testv.wav"
sample_rate = get_sample_rate(file_path)
print(f"Sample Rate: {sample_rate} Hz")


transcribe_file("utils/output.raw")