from utils.download import download_audio

url = input("Enter video URL: ")
audio_path = download_audio(url)
print("Audio downloaded at:", audio_path)
