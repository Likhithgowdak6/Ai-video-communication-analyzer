# app.py (updated to match your utils filenames)
import streamlit as st
import os
import traceback

# import the functions that exist in your utils folder
try:
    from utils.download import download_audio
except Exception:
    download_audio = None

try:
    from utils.transcribe_local import transcribe_local
except Exception:
    transcribe_local = None

try:
    from utils.analysis_local_llm import analyze_transcript
except Exception:
    analyze_transcript = None

st.set_page_config(page_title="AI Video Communication Analyzer", layout="centered")
st.title("🎙️ AI Video Communication Analyzer")
st.write("Enter a YouTube video URL (or paste a local audio/video path). The app downloads audio, transcribes locally and shows Clarity, Focus, Summary.")

PLACEHOLDER = "https://www.youtube.com/watch?v=8FiEKMxZN0s"

video_input = st.text_input("Video URL or local file path", placeholder=PLACEHOLDER)

if st.button("Analyze Video"):
    if not video_input or not video_input.strip():
        st.error("Please enter a URL or a valid local file path.")
        st.stop()

    # Verify required utils are available
    if download_audio is None:
        st.error("utils.download.download_audio not found. Check utils/download.py")
        st.stop()
    if transcribe_local is None:
        st.error("utils.transcribe_local.transcribe_local not found. Check utils/transcribe_local.py")
        st.stop()
    if analyze_transcript is None:
        st.error("utils.analysis_local_llm.analyze_transcript not found. Check utils/analysis_local_llm.py")
        st.stop()

    # Clean previous artifacts to avoid stale reuse
    def safe_remove(path):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    safe_remove("audio_input.m4a")
    safe_remove("transcript.txt")

    st.info("Starting pipeline...")

    # If local file path exists, use it directly (allow video or audio file)
    if os.path.exists(video_input) and os.path.isfile(video_input):
        st.write(f"Using local file: {video_input}")
        audio_path = video_input
    else:
        # treat input as URL -> download audio
        st.write("Detected input as URL. Downloading audio (bestaudio)...")
        try:
            # download_audio returns the downloaded audio filepath
            audio_path = download_audio(video_input)
            st.success(f"Audio downloaded: {audio_path}")
        except Exception as e:
            st.error("Audio download failed. See details below.")
            st.text(traceback.format_exc())
            st.stop()

    # Transcribe (always re-transcribe the chosen audio file)
    st.write("Transcribing (local Whisper)... this may take time for large models.")
    try:
        transcript_text = transcribe_local(audio_path)
        # save transcript
        with open("transcript.txt", "w", encoding="utf-8") as f:
            f.write(transcript_text)
        st.success("Transcription completed and saved to transcript.txt")
    except Exception as e:
        st.error("Transcription failed. See details below.")
        st.text(traceback.format_exc())
        st.stop()

    # Analyze (clarity, focus, short summary)
    st.write("Analyzing transcript for Clarity, Focus and Short Summary...")
    try:
        # prefer_hf False -> use local deterministic analysis by default
        clarity, focus, summary, raw = analyze_transcript(transcript_text, prefer_hf=False)
    except TypeError:
        # older signature fallback
        clarity, focus, summary, raw = analyze_transcript(transcript_text)
    except Exception:
        st.error("Analysis failed. See details below.")
        st.text(traceback.format_exc())
        st.stop()

    # Display results
    st.subheader("📊 Results")
    st.metric("Clarity Score (0–100)", f"{clarity}")
    st.write("### 🎯 Communication Focus (one sentence)")
    st.write(focus)
    st.write("### 📝 Short Summary (2–3 lines)")
    st.write(summary)

    with st.expander("🔎 Raw/Debug Output"):
        try:
            st.json(raw)
        except Exception:
            st.text(str(raw))
        st.write("Audio used:", audio_path)
        st.write("Transcript file: transcript.txt")
