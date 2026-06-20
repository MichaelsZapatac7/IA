"""
Auto-caption generation using OpenAI Whisper (local, free).
Produces SRT subtitle files from audio/video.
"""

import subprocess
import json
from pathlib import Path
from typing import Optional


def transcribe_with_whisper(
    audio_path: Path,
    output_dir: Path,
    model: str = "base",
    language: Optional[str] = None,
) -> Path:
    """
    Transcribe audio using the `whisper` CLI tool and produce an SRT file.
    Returns the path to the .srt file.

    Args:
        audio_path: Path to audio or video file
        output_dir: Directory where SRT will be saved
        model: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        language: Force language (e.g. 'es', 'en'). Auto-detects if None.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "whisper", str(audio_path),
        "--model", model,
        "--output_dir", str(output_dir),
        "--output_format", "srt",
    ]
    if language:
        cmd += ["--language", language]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Whisper failed: {result.stderr[-500:]}")

    # Whisper saves the file as {audio_name}.srt
    srt_path = output_dir / (audio_path.stem + ".srt")
    if not srt_path.exists():
        raise FileNotFoundError(f"Expected SRT at {srt_path} but not found. Whisper output: {result.stdout[-200:]}")
    return srt_path


def transcribe_with_api(
    audio_path: Path,
    output_dir: Path,
    anthropic_api_key: str,
    language: Optional[str] = "es",
) -> Path:
    """
    Fallback: Use the OpenAI Whisper API for transcription.
    Requires the openai package: pip install openai
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("pip install openai  (needed for API-based transcription)")

    client = OpenAI()
    with open(audio_path, "rb") as f:
        params = {"model": "whisper-1", "response_format": "srt"}
        if language:
            params["language"] = language
        srt_content = client.audio.transcriptions.create(file=f, **params)

    output_dir.mkdir(parents=True, exist_ok=True)
    srt_path = output_dir / (audio_path.stem + ".srt")
    srt_path.write_text(srt_content, encoding="utf-8")
    return srt_path


def segments_to_srt(segments: list[dict], audio_paths: list[Path], output_path: Path) -> Path:
    """
    Build an SRT from script segments + per-segment audio duration.
    Used when Whisper is not available — creates approximate timing.
    """
    lines = []
    cursor = 0.0

    for i, (segment, audio_path) in enumerate(zip(segments, audio_paths), start=1):
        # Estimate duration from audio file via ffprobe
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "csv=p=0", str(audio_path)],
                capture_output=True, text=True
            )
            duration = float(result.stdout.strip())
        except Exception:
            duration = segment.get("duration_seconds", 10)

        start = _seconds_to_srt_time(cursor)
        end = _seconds_to_srt_time(cursor + duration)
        text = segment.get("text", "").strip()

        # Split long lines for readability
        words = text.split()
        chunks = []
        chunk = []
        for word in words:
            chunk.append(word)
            if len(" ".join(chunk)) > 50:
                chunks.append(" ".join(chunk))
                chunk = []
        if chunk:
            chunks.append(" ".join(chunk))
        display_text = "\n".join(chunks)

        lines.append(f"{i}\n{start} --> {end}\n{display_text}\n")
        cursor += duration

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def _seconds_to_srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
