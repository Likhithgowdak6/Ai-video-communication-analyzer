from faster_whisper import WhisperModel

def transcribe_local(audio_path):
    print("[LOCAL] Loading Whisper model... (large-v3-turbo)")
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="float32")

    print("[LOCAL] Transcribing audio...")
    segments, info = model.transcribe(audio_path)

    print(f"[LOCAL] Language: {info.language}, Duration: {info.duration}")

    final_text = "\n".join([seg.text for seg in segments])
    return final_text
