import webrtcvad
import wave
import collections

def read_wave(filepath):
    """Reads a .wav file and returns (PCM audio data, sample rate)."""
    with wave.open(filepath, 'rb') as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1, "Audio file must be mono."
        sample_width = wf.getsampwidth()
        assert sample_width == 2, "Audio sample width must be 16-bit."
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000), "Sample rate must be 8, 16, or 32 kHz."
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate

def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data."""
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    while offset + n <= len(audio):
        yield audio[offset:offset + n]
        offset += n

class Frame(object):
    """Represents a frame of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration

def vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
    """Filters out non-voiced audio frames using WebRTC's VAD."""
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False

    voiced_frames = []
    for frame in frames:
        is_speech = vad.is_speech(frame, sample_rate)

        if triggered:
            voiced_frames.append(frame)
            if not is_speech:
                triggered = False
        elif is_speech:
            triggered = True
            ring_buffer.clear()
            voiced_frames.extend(ring_buffer)
            voiced_frames.append(frame)
        else:
            ring_buffer.append(frame)
    
    return b''.join(voiced_frames)

def process_vad(filepath, aggressiveness=3):
    """Processes an audio file and returns voiced segments."""
    audio, sample_rate = read_wave(filepath)
    vad = webrtcvad.Vad(aggressiveness)

    frames = frame_generator(30, audio, sample_rate)
    vad_segments = vad_collector(sample_rate, 30, 300, vad, frames)
    return vad_segments

