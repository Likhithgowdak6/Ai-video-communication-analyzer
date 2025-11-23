# utils/download.py — compact downloader suitable for local deployment
import os
import subprocess
import time
from typing import Tuple

AUDIO_EXTS = (".m4a", ".mp3", ".webm", ".wav", ".aac", ".opus", ".ogg")

def _is_url(s: str) -> bool:
    return bool(s) and s.strip().lower().startswith(("http://", "https://", "ftp://"))

def _find_newest_audio(out_dir: str = ".", prefix: str = "audio_input_"):
    files = [os.path.join(out_dir, f) for f in os.listdir(out_dir)
             if f.startswith(prefix) and f.lower().endswith(AUDIO_EXTS)]
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def download_audio(input_path_or_url: str, out_dir: str = ".", timeout: int = 600) -> Tuple[str, str]:
    """
    Returns (filepath, None) on success or (None, error_message) on failure.
    Quick and safe for local usage.
    """
    if not input_path_or_url:
        return None, "No input provided."

    inp = input_path_or_url.strip()

    # If local file exists, use it directly.
    if os.path.isfile(inp):
        return os.path.abspath(inp), None

    # If not a URL, fail quickly.
    if not _is_url(inp):
        return None, f"Not a file and not a URL: {inp}"

    # Prepare simple yt-dlp command to fetch best audio (one attempt)
    ts = int(time.time())
    out_template = os.path.join(out_dir, f"audio_input_{ts}.%(ext)s")
    cmd = [
        "yt-dlp",
        "-f", "bestaudio[ext=m4a]/bestaudio/best",
        "--output", out_template,
        "--restrict-filenames",
        inp
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        stderr = proc.stderr.decode(errors="ignore")
        if proc.returncode != 0:
            if "403" in stderr or "403 Forbidden" in stderr:
                return None, "HTTP 403: remote host blocked the download."
            return None, f"yt-dlp failed: {stderr.splitlines()[-5:]}"
        # find the produced audio file
        found = _find_newest_audio(out_dir)
        if found:
            return os.path.abspath(found), None
        return None, "yt-dlp finished but no audio file found."
    except FileNotFoundError:
        return None, "yt-dlp not installed. Install yt-dlp for URL downloads."
    except subprocess.TimeoutExpired:
        return None, f"Download timed out after {timeout} seconds."
    except Exception as e:
        return None, f"Unexpected error: {e}"
