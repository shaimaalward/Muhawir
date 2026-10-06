from __future__ import annotations

import json
import re
import shutil
import subprocess

from .models import VoiceMetrics


ARABIC_FILLERS = [
    "يعني", "اممم", "أمم", "ممم", "اه", "آه", "ااا", "إمم", "طيب"
]


def _duration_seconds(path: str) -> float | None:
    if not shutil.which("ffprobe"):
        return None
    try:
        proc = subprocess.run(
            [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", path,
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )
        data = json.loads(proc.stdout)
        return float(data["format"]["duration"])
    except Exception:
        return None


def _silence_counts(path: str) -> tuple[int | None, int | None]:
    """Counts observable pauses using ffmpeg silencedetect.

    pause_count: silence >= 0.7 s
    long_pause_count: silence >= 1.5 s
    """
    if not shutil.which("ffmpeg"):
        return None, None
    try:
        proc = subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-i", path,
                "-af", "silencedetect=noise=-35dB:d=0.7",
                "-f", "null", "-",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        stderr = proc.stderr
        starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", stderr)]
        ends = re.findall(r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)", stderr)
        durations = [float(d) for _, d in ends]
        pause_count = max(len(starts), len(durations))
        long_count = sum(1 for d in durations if d >= 1.5)
        return pause_count, long_count
    except Exception:
        return None, None


def analyze_voice(path: str, transcript: str) -> VoiceMetrics:
    duration = _duration_seconds(path)
    words = [w for w in re.split(r"\s+", transcript.strip()) if w]
    filler_words: dict[str, int] = {}
    for filler in ARABIC_FILLERS:
        count = len(re.findall(rf"(?<!\w){re.escape(filler)}(?!\w)", transcript, flags=re.IGNORECASE))
        if count:
            filler_words[filler] = count
    filler_count = sum(filler_words.values())
    wpm = None
    if duration and duration > 0:
        wpm = len(words) / duration * 60.0
    pause_count, long_pause_count = _silence_counts(path)
    return VoiceMetrics(
        duration_seconds=round(duration, 2) if duration else None,
        word_count=len(words),
        words_per_minute=round(wpm, 1) if wpm else None,
        filler_count=filler_count,
        filler_words=filler_words,
        pause_count=pause_count,
        long_pause_count=long_pause_count,
        transcript_available=bool(transcript.strip()),
    )
