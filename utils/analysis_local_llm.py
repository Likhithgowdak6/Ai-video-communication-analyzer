# utils/analysis_local_llm.py — minimal deterministic analyzer
import re

def _tokenize_words(text):
    return re.findall(r"[A-Za-z0-9']+", (text or "").lower())

def _split_sentences(text):
    parts = re.split(r'(?<=[.!?])\s+', (text or "").strip())
    return [p.strip() for p in parts if p.strip()]

_FILLERS = {"um","uh","like","actually","basically","right","well","hmm","okay","you","i"}

def compute_clarity_score(text):
    if not text or not text.strip():
        return 0
    words = _tokenize_words(text)
    n = max(1, len(words))
    fillers = sum(1 for w in words if w in _FILLERS)
    avg_len = 0
    sents = _split_sentences(text)
    if sents:
        avg_len = sum(len(_tokenize_words(s)) for s in sents) / max(1, len(sents))
    score = 100.0
    score -= (fillers / n) * 60.0
    if avg_len < 4:
        score -= (4 - avg_len) * 5.0
    elif avg_len > 25:
        score -= (avg_len - 25) * 1.0
    if n < 12:
        score -= 5
    return max(0, min(100, int(round(score))))

_STOP = {"the","a","an","in","on","of","and","to","is","it","that","this","for","with","as","are","was","were","you","i","we","they","he","she","but"}

def extract_focus_sentence(text, max_words=28):
    if not text or not text.strip():
        return ""
    sents = _split_sentences(text)
    if not sents:
        return ""
    freq = {}
    for w in _tokenize_words(text):
        if w in _STOP or len(w) < 3:
            continue
        freq[w] = freq.get(w, 0) + 1
    scored = []
    for idx, s in enumerate(sents):
        toks = _tokenize_words(s)
        score = sum(freq.get(w,0) for w in toks)
        if score > 0:
            scored.append((score/ max(1, (len(toks)**0.5)), idx, s))
    if not scored:
        return sents[0][:200].rstrip(' .')
    scored.sort(reverse=True)
    best = scored[0][2].strip().rstrip(' .')
    toks = _tokenize_words(best)
    if len(toks) > max_words:
        return " ".join(toks[:max_words]) + "..."
    return best

def generate_short_summary_local(text, max_sentences=2):
    if not text or not text.strip():
        return ""
    sents = _split_sentences(text)
    if not sents:
        return ""
    # simple: pick the top-frequency sentences by content words
    freq = {}
    for w in _tokenize_words(text):
        if w in _STOP or len(w) < 3:
            continue
        freq[w] = freq.get(w,0) + 1
    scored = []
    for i,s in enumerate(sents):
        toks = _tokenize_words(s)
        score = sum(freq.get(w,0) for w in toks)
        scored.append((score, i, s))
    scored.sort(key=lambda x: (-x[0], x[1]))
    chosen = []
    for sc,i,s in scored:
        if len(chosen) >= max_sentences:
            break
        if len(_tokenize_words(s)) < 6:
            continue
        chosen.append(s)
    if not chosen:
        # fallback: first two reasonable sentences
        out = []
        for s in sents:
            if len(_tokenize_words(s)) >= 6:
                out.append(s)
            if len(out) >= max_sentences:
                break
        return " ".join(out)
    return " ".join(chosen)

def analyze_transcript(transcript_text):
    """
    Returns clarity (int), focus (str), summary (str), meta (dict)
    """
    meta = {"mode": "local"}
    if not transcript_text or not transcript_text.strip():
        meta.update({"clarity": 0, "focus": "", "summary": ""})
        return 0, "", "", meta
    clarity = compute_clarity_score(transcript_text)
    focus = extract_focus_sentence(transcript_text)
    summary = generate_short_summary_local(transcript_text, max_sentences=2)
    meta.update({"clarity": clarity, "focus": focus, "summary": summary})
    return clarity, focus, summary, meta
