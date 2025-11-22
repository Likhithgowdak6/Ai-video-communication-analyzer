# utils/download.py
import subprocess
import time
import glob
import os

def download_audio(url, output_name=None):
    """
    Download only audio with yt-dlp and return the local audio file path.
    If output_name is None, create a timestamped filename audio_input_<ts>.<ext>.
    """
    ts = int(time.time())
    # let yt-dlp pick extension, we'll use a template with timestamp placeholder
    if output_name:
        # user-specified exact output name (should include %(ext)s)
        out_template = output_name
    else:
        out_template = f"audio_input_{ts}.%(ext)s"

    cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "-o", out_template,
        url
    ]

    print("[INFO] Download command:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        raise RuntimeError("yt-dlp failed to download audio.")

    # find the downloaded file matching the pattern (timestamp)
    # out_template uses the timestamp so glob should match
    base = out_template.split("%")[0]  # e.g. "audio_input_168..._."
    # but safer: search for files starting with audio_input_{ts}
    pattern = f"audio_input_{ts}.*"
    files = glob.glob(pattern)
    if not files:
        # fallback: maybe user provided literal output_name without %(ext)s
        if output_name and os.path.exists(output_name):
            return output_name
        raise RuntimeError("Downloaded file not found after yt-dlp run.")
    # choose first match
    audio_path = files[0]
    print(f"[DONE] Audio saved: {audio_path}")
    return audio_path
