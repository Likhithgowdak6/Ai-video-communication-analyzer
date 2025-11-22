# utils/download.py — Minimal robust downloader
import os
import subprocess
import time
from typing import Tuple

def _is_remote(s: str) -> bool:
    if not s:
        return False
    s = s.strip().lower()
    return s.startswith("http://") or s.startswith("https://") or s.startswith("ftp://")

def _newest_audio_file_in_dir(out_dir: str, prefix="audio_input_"):
    exts = [".m4a", ".mp3", ".webm", ".wav", ".aac", ".opus", ".ogg"]
    cand = []
    for fn in os.listdir(out_dir):
        if fn.startswith(prefix) and any(fn.lower().endswith(ext) for ext in exts):
            cand.append(os.path.join(out_dir, fn))
    if not cand:
        return None
    return os.path.abspath(sorted(cand, key=lambda p: os.path.getmtime(p), reverse=True)[0])

def download_audio(input_url_or_path: str, out_dir: str = ".", max_retries: int = 1, timeout: int = 600) -> Tuple[str, str]:
    """
    Returns (filepath, None) on success or (None, error_message) on failure.
    If input is a local existing file, returns it immediately.
    """
    if not input_url_or_path:
        return None, "No input provided."
    inp = input_url_or_path.strip()
    # local path?
    if os.path.exists(inp) and os.path.isfile(inp):
        return os.path.abspath(inp), None
    if not _is_remote(inp):
        return None, f"Input not a file and not a URL: {inp}"

    ts = int(time.time())
    out_template = os.path.join(out_dir, f"audio_input_{ts}.%(ext)s")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    base_cmd = [
        "yt-dlp",
        "-f", "bestaudio[ext=m4a]/bestaudio/best",
        "--extractor-args", "youtube:player_client=default",
        "--output", out_template,
        "--restrict-filenames",
        "--no-warnings",
        "--no-check-certificate",
        "--user-agent", user_agent
    ]

    attempt = 0
    last_err = None
    while attempt <= max_retries:
        attempt += 1
        try:
            proc = subprocess.run(base_cmd + [inp], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            stderr = proc.stderr.decode(errors="ignore")
            if proc.returncode == 0:
                found = _newest_audio_file_in_dir(out_dir, prefix="audio_input_")
                if found:
                    return found, None
                last_err = "yt-dlp finished but produced no file."
                break
            else:
                if "HTTP Error 403" in stderr or "403 Forbidden" in stderr:
                    last_err = ("HTTP 403 Forbidden from remote host. YouTube may block automated downloads or require a JS runtime.")
                    break
                last_err = stderr.splitlines()[-8:]
        except FileNotFoundError:
            last_err = "yt-dlp not found in environment."
            break
        except subprocess.TimeoutExpired:
            last_err = f"Download timed out after {timeout}s."
        except Exception as e:
            last_err = f"Unexpected error: {e}"
        time.sleep(1 + attempt)
    # fallback: find any recent audio_input_* file
    fallback = _newest_audio_file_in_dir(out_dir, prefix="audio_input_")
    if fallback:
        return fallback, None
    return None, (last_err or "Unknown download error.")
