# app.py — Minimal stable Streamlit app
import os
import traceback
import streamlit as st

from utils.download import download_audio
from utils.transcribe_local import transcribe_local
from utils.analysis_local_llm import analyze_transcript

st.set_page_config(page_title="AI Video Communication Analyzer", layout="centered")
st.title("🎙️ AI Video Communication Analyzer")
st.write("Paste a YouTube URL or choose/upload a local audio/video file. "
         "The app downloads/transcribes audio and shows Clarity, Focus, and Summary.")

DEFAULT_URL = "https://www.youtube.com/watch?v=8FiEKMxZN0s"
video_input = st.text_input("Video URL or Local File Path", placeholder=DEFAULT_URL)

uploaded_file = st.file_uploader("Or upload an audio/video file (mp4,m4a,mp3,wav,webm)", type=["mp4","m4a","mp3","wav","webm"])

def safe_remove(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except:
        pass

if st.button("Analyze"):
    # cleanup old artifacts
    safe_remove("transcript.txt")
    safe_remove("uploaded_input")

    # pick audio source: uploaded file -> local path -> URL download
    audio_path = None
    if uploaded_file is not None:
        # save uploaded file
        with open("uploaded_input", "wb") as f:
            f.write(uploaded_file.getbuffer())
        audio_path = os.path.abspath("uploaded_input")
        st.success("Using uploaded file.")
    elif video_input and os.path.exists(video_input) and os.path.isfile(video_input):
        audio_path = os.path.abspath(video_input)
        st.success(f"Using local file: {audio_path}")
    else:
        # treat as URL
        if not video_input or not video_input.strip():
            st.error("Please provide a URL, a local path, or upload a file.")
            st.stop()
        st.info("Downloading audio from URL...")
        audio_path, err = download_audio(video_input)
        if not audio_path:
            st.error("Audio download failed.")
            st.warning(str(err))
            st.info("Options: upload a file, try a different URL, or enable Demo Mode.")
            st.stop()
        st.success(f"Audio downloaded: {audio_path}")

    # transcribe
    st.info("Transcribing audio (local Whisper)... this may take time.")
    try:
        transcript = transcribe_local(audio_path)
        with open("transcript.txt", "w", encoding="utf-8") as f:
            f.write(transcript)
        st.success("Transcription completed.")
    except Exception:
        st.error("Transcription error — see debug below.")
        st.text(traceback.format_exc())
        st.stop()

    # analyze
    st.info("Analyzing transcript...")
    try:
        clarity, focus, summary, meta = analyze_transcript(transcript)
    except Exception:
        st.error("Analysis failed.")
        st.text(traceback.format_exc())
        st.stop()

    # show results
    st.subheader("📊 Results")
    st.metric("Clarity Score (0–100)", clarity)
    st.write("### 🎯 Communication Focus")
    st.write(focus)
    st.write("### 📝 Short Summary")
    st.write(summary)

    with st.expander("🔎 Debug / Meta"):
        st.json(meta)
        st.write("Audio used:", audio_path)
        st.write("Transcript file: transcript.txt")
