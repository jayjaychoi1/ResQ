import wave
import webrtcvad

# 파일 경로
file_path = 'outbound.wav'

# WebRTC VAD 설정
vad = webrtcvad.Vad()
vad.set_mode(3)  # 가장 엄격한 탐지

# 10ms 단위로 PCM 데이터를 처리하는 함수
def process_audio_with_vad(file_path, vad, frame_duration_ms=10):
    with wave.open(file_path, 'rb') as wf:
        num_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        frame_rate = wf.getframerate()

        # WebRTC VAD는 Mono 채널만 지원하므로 확인
        if num_channels != 1:
            raise ValueError("WebRTC VAD only supports mono audio.")
        if sample_width != 2:
            raise ValueError("WebRTC VAD only supports 16-bit PCM audio.")

        # 10ms 프레임 크기 계산
        frame_size = int(frame_rate * frame_duration_ms / 1000) * 2  # 샘플 당 2바이트
        audio_data = wf.readframes(wf.getnframes())

        # 10ms 단위로 VAD 적용
        results = []
        for i in range(0, len(audio_data), frame_size):
            frame = audio_data[i:i+frame_size]
            if len(frame) < frame_size:
                continue  # 마지막 프레임이 작으면 건너뜀
            is_speech = vad.is_speech(frame, frame_rate)
            results.append(is_speech)
        return results

# VAD 결과 확인
vad_results = process_audio_with_vad(file_path, vad)

# 출력: 프레임 단위로 음성인지 여부 표시
print(vad_results[:100])  # 처음 100개의 결과를 출력