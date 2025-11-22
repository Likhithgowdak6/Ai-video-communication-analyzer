# utils/transcribe_local.py — lightweight wrapper for faster-whisper
import os
import traceback
from faster_whisper import WhisperModel

def transcribe_local(audio_path: str) -> str:
    """
    Transcribe with faster-whisper. Model selected via WHISPER_MODEL env var (default: "small").
    Returns transcript text (empty string on failure).
    """
    model_name = os.environ.get("WHISPER_MODEL", "small")  # use "small" on Streamlit Cloud for demo
    try:
        model = WhisperModel(model_name, device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path)
        text = "\n".join(seg.text for seg in segments)
        return text
    except Exception:
        # return a helpful error string rather than crash the app
        tb = traceback.format_exc()
        return f"[TRANSCRIPTION ERROR]\n{tb}"
