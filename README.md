# 🎙️ **AI Video Communication Analyzer**

*A local end-to-end pipeline for downloading audio, transcribing it with Whisper, and generating clarity, focus, and summary insights.*

## ⭐ **Overview**

https://github.com/user-attachments/assets/63c42cd3-0e93-46f5-afc1-ba6e42e43f1d



This project analyzes communication quality from any **YouTube video URL** or **local audio/video file**.

It performs:

1. **Audio Extraction**
2. **Transcription (Faster-Whisper — fully local, offline)**
3. **Communication Analysis:**

   * Clarity Score
   * One-sentence Focus
   * Short Summary

This tool is ideal for analyzing motivational talks, presentations, interviews, or speeches.

## 🚀 **Features**

* 🎥 Accepts **YouTube URLs** or **local audio/video paths**
* 🎧 Automatically downloads **best audio format**
* 📝 Local transcription using **Whisper (large-v3-turbo)**
* 📊 Natural language analysis without any API
* 🔍 Debug panel for raw outputs
* ⚡ Minimal, stable, and deployment-friendly codebase


## 🗂️ **Project Structure**


ai-video-communication-analyzer/
│
├── app.py                     # Streamlit main application
├── requirements.txt           # Dependencies
│
└── utils/
    ├── download.py            # Clean yt-dlp audio downloader
    ├── transcribe_local.py    # Faster-Whisper transcription
    └── analysis_local_llm.py  # Clarity, focus, summary analysis
```


## 💻 **Local Setup Guide (Windows)**

### 1️⃣ **Clone the Repo**


git clone https://github.com/Likhithgowdak6/Ai-video-communication-analyzer
cd ai-video-communication-analyzer
```

### 2️⃣ **Create & Activate Virtual Environment**

```
python -m venv env
env\Scripts\activate
```

### 3️⃣ **Install Dependencies**

```
pip install -r requirements.txt
```

### 4️⃣ **Install system dependencies**

Whisper needs FFmpeg.
Download FFmpeg for Windows:
[https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)

Extract → Copy `ffmpeg.exe` into PATH or inside project folder.

### 5️⃣ **Run the App**

```
streamlit run app.py
```
## 🧠 **How the Pipeline Works**

### **Step 1: Input Detection**

User enters:

* a YouTube URL
* OR a local file path (MP4, M4A, WAV, etc.)

If the file exists → skip download
Else → treat it as URL.

---

### **Step 2: Audio Extraction**

Handled by `utils/download.py`:

* Uses **yt-dlp**
* Downloads **bestaudio** format
* Ignores JS runtime issues
* Returns file like:

  ```
  audio_input_1763832456.m4a
  ```

If download fails → returns clean error message.

---

### **Step 3: Transcription**

`utils/transcribe_local.py`:

* Loads **faster-whisper (large-v3-turbo)**
* Runs **local transcription**
* Outputs `transcript.txt`

---

### **Step 4: Text Analysis**

`utils/analysis_local_llm.py` performs:

* Word tokenizing
* Sentence segmentation
* Repetition compression
* Filler count
* Extracts focus sentence
* Generates 2–3 line summary
* Produces clarity score (0–100)

No external LLM or API required.

---

### **Step 5: UI Output**

* Clarity Score meter
* Communication Focus (1 line)
* Short Summary
* Expandable debug info

---

## 🧩 **File Management**

The app auto-manages:

```
transcript.txt                  # Latest transcript
audio_input_<timestamp>.*       # Auto-generated audio files
```

On every run:

* Old audio files are ignored
* Old transcript is removed
* New timestamped audio is used

---

## 📦 **requirements.txt**

```
streamlit
yt-dlp
faster-whisper==1.0.3
numpy
python-dotenv
requests
tqdm
soundfile
ffmpeg-python
```

## ⚠️ **Common Issues**

### ❌ yt-dlp failed to download audio

✔ Try using a different YouTube URL
✔ Try running locally (Streamlit Cloud may block downloads)

### ❌ faster-whisper model too large

Large models may take time to load—first run is slow.

### ❌ FFmpeg not found

Install ffmpeg manually and add to PATH.

---

## 🌐 **Deployment Notes**

### Streamlit Cloud

❌ Not supported — cannot install system-level libraries required for Whisper (`av`, `pkg-config`, FFmpeg).

### Flask Deployment

✔ Works on any cloud VM with FFmpeg + Python
❌ Requires access to AWS / Render / Railway / GCP to install system dependencies.

If needed, future-ready deployment scripts can be added.

---

## 🏁 **Conclusion**

This project delivers a fully functional **local AI communication analysis pipeline**, with:

* Clear modular structure
* Minimal dependencies
* Local LLM-free analysis
* Whisper transcription
* Clean Streamlit UI
