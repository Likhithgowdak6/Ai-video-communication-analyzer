# utils/analysis_local_llm.py
"""
Minimal analysis module — local deterministic-only.
Provides:
 - compute_clarity_score(text) -> int 0-100
 - extract_focus_sentence(text) -> short sentence
 - generate_short_summary_local(text) -> 1-3 lines
 - analyze_transcript(text) -> (clarity, focus, summary, metadata)
No external API calls or optional features included.
"""

import re
import json

# ---------- Simple helpers ----------
def _tokenize_words(text):
    return re.findall(r"\w+", (text or "").lower())

def _split_sentences(text):
    parts = re.split(r'(?<=[.!?])\s+', (text or "").strip())
    return [p.strip() for p in parts if p.strip()]

def compress_repeated_phrases(text, max_repeat_len=6):
    if not text:
        return text
    words = re.findall(r'\S+', text)
    n = len(words)
    for L in range(min(max_repeat_len, n), 0, -1):
        i = 0
        out = []
        while i < n:
            if i + L <= n:
                phrase = tuple(words[i:i+L])
                j = i + L
                repeat = 1
                while j + L <= n and tuple(words[j:j+L]) == phrase:
                    repeat += 1
                    j += L
                if repeat > 1:
                    out.extend(phrase)
                    i = j
                    continue
            out.append(words[i])
            i += 1
        words = out
        n = len(words)
    text = " ".join(words)
    text = re.sub(r'\b(\w+)(?:\s+\1){2,}\b', r'\1', text, flags=re.I)
    return re.sub(r'\s+', ' ', text).strip()

# ---------- Clarity ----------
_FILLERS = {"um","uh","like","actually","basically","right","well","hmm","okay"}
def _count_fillers(text):
    words = _tokenize_words(text)
    return sum(1 for w in words if w in _FILLERS)

def _average_sentence_length(text):
    sents = _split_sentences(text)
    if not sents:
        return 0.0
    lengths = [len(_tokenize_words(s)) for s in sents]
    return sum(lengths) / max(1, len(lengths))

def _repetition_penalty(text):
    words = _tokenize_words(text)
    return sum(1 for i in range(1, len(words)) if words[i] == words[i-1])

def compute_clarity_score(text):
    if not text or not text.strip():
        return 0
    text = compress_repeated_phrases(text)
    words = _tokenize_words(text)
    n = max(1, len(words))
    fillers = _count_fillers(text)
    avg_len = _average_sentence_length(text)
    repeats = _repetition_penalty(text)

    score = 100.0
    score -= (fillers / n) * 200.0
    score -= repeats * 2.5
    if avg_len < 6:
        score -= (6 - avg_len) * 3.0
    elif avg_len > 20:
        score -= (avg_len - 20) * 1.5
    if n < 30:
        score -= 5
    return max(0, min(100, int(round(score))))

# ---------- Focus extraction ----------
_STOP = {"the","a","an","in","on","of","and","to","is","it","that","this","for","with","as","are","was","were","you","i","we","they","he","she","but"}
def extract_focus_sentence(text, max_words=25):
    if not text or not text.strip():
        return ""
    text = compress_repeated_phrases(text)
    sents = _split_sentences(text)
    if not sents:
        return ""
    # keyword freq
    freq = {}
    for w in _tokenize_words(text):
        if w in _STOP:
            continue
        freq[w] = freq.get(w, 0) + 1
    scored = []
    for idx, s in enumerate(sents):
        toks = _tokenize_words(s)
        if not toks:
            continue
        sc = sum(freq.get(w, 0) for w in toks)
        penalty = max(0, len(toks) - 20) * 0.5
        scored.append((sc - penalty, idx, s))
    scored.sort(key=lambda x: (-x[0], x[1]))
    for sc, idx, s in scored:
        toks = _tokenize_words(s)
        if 4 <= len(toks) <= max_words:
            return s.strip().rstrip(' .')
    if scored:
        best = scored[0][2]
        toks = _tokenize_words(best)
        if len(toks) > max_words:
            return " ".join(toks[:max_words]).strip() + "..."
        return best.strip().rstrip(' .')
    return ""

# ---------- Short summary ----------
def generate_short_summary_local(text, max_sentences=2):
    if not text or not text.strip():
        return ""
    text = compress_repeated_phrases(text)
    sents = _split_sentences(text)
    if not sents:
        return ""
    freq = {}
    for w in _tokenize_words(text):
        if w in _STOP:
            continue
        freq[w] = freq.get(w, 0) + 1
    scored = []
    for i, s in enumerate(sents):
        toks = _tokenize_words(s)
        sc = sum(freq.get(w, 0) for w in toks if w not in _STOP)
        if len(toks) < 4:
            sc *= 0.5
        scored.append((sc, i, s))
    scored_sorted = sorted(scored, key=lambda x: (-x[0], x[1]))
    chosen = []
    for sc, idx, s in scored_sorted:
        cand = re.sub(r'\W+', ' ', s).strip().lower()
        dup = False
        for ci in chosen:
            prev = re.sub(r'\W+', ' ', sents[ci]).strip().lower()
            set_c = set(cand.split())
            set_p = set(prev.split())
            if len(set_c & set_p) / max(1, len(set_c | set_p)) > 0.6:
                dup = True
                break
        if dup:
            continue
        if len(_tokenize_words(s)) < 6:
            continue
        chosen.append(idx)
        if len(chosen) >= max_sentences:
            break
    if not chosen:
        selected = []
        for s in sents:
            if len(_tokenize_words(s)) >= 6:
                selected.append(s)
            if len(selected) >= max_sentences:
                break
        return " ".join(selected[:max_sentences]).strip()
    chosen = sorted(chosen)
    selected = [sents[i] for i in chosen]
    summary = " ".join(selected)
    summary = compress_repeated_phrases(summary)
    summary = re.sub(r'\s+', ' ', summary).strip()
    if len(summary) > 400:
        cut = summary[:350]
        if '.' in cut:
            cut = cut.rsplit('.', 1)[0] + '.'
        else:
            cut = cut[:350].rsplit(' ', 1)[0] + "..."
        return cut
    return summary

# ---------- Public API ----------
def analyze_transcript(transcript_text):
    """
    Returns: (clarity_int, focus_str, short_summary_str, metadata_json_str)
    """
    if not transcript_text or not transcript_text.strip():
        meta = {"mode": "local", "clarity": 0, "focus": "", "summary": ""}
        return 0, "", "", json.dumps(meta)
    clarity = compute_clarity_score(transcript_text)
    focus = extract_focus_sentence(transcript_text)
    summary = generate_short_summary_local(transcript_text, max_sentences=2)
    meta = {"mode": "local", "clarity": clarity, "focus": focus, "summary": summary}
    return clarity, focus, summary, json.dumps(meta)
