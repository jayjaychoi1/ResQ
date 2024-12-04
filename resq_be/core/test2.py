async def handle_messages(self):
    """Handle messages from Twilio WebSocket."""
    try:
        async for message in self.twilio_ws.iter_text():
            event = json.loads(message)
            event_type = event["event"]
            if event_type == "start":
                self.stream_id = event["start"]["streamSid"]
                self.call_id = event["start"]["callSid"]
                self.account_id = event["start"]["accountSid"]
            if event_type == "media":
                # Decode the Base64 payload to raw G.711 µ-law bytes
                payload = event["media"]["payload"]
                ulaw_chunk = base64.b64decode(payload)

                # Convert µ-law to linear PCM (16-bit)
                pcm_chunk = audioop.ulaw2lin(ulaw_chunk, 2)  # 2 means 16-bit PCM

                self.pcm_data[event["media"]["track"]].extend(pcm_chunk)
            if event_type == "stop":
                self.export_audio()
                break


def export_audio(self):
    """Export the recorded audio to an MP3 file."""
    try:
        audio_segments = {}
        for track in self.pcm_data:
            audio_segment = AudioSegment(
                data=bytes(self.pcm_data[track]),
                sample_width=2,  # 16-bit audio
                frame_rate=8000,  # G.711 µ-law is usually sampled at 8 kHz
                channels=1,  # mono audio
            )
            audio_segments[track] = audio_segment
        combined_audio = audio_segments["inbound"].overlay(
            audio_segments["outbound"]
        )
        combined_audio.export(
            os.path.join(self.export_path, f"{self.call_id}_twilio.mp3"),
            format="mp3",
        )