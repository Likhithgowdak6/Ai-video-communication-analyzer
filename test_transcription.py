from utils.transcribe_local import transcribe_local

audio_path = "audio_input.m4a"

print("🔊 Starting local Whisper transcription...")
text = transcribe_local(audio_path)

print("\n--- TRANSCRIPT ---\n")
print(text)
