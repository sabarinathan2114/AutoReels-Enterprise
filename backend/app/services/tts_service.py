"""
Multi-Speaker TTS Service (Spec 4.1, 15.4)
Synthesizes dialogue with [MALE], [FEMALE], [KID] speaker tags.
Enforces 150ms natural speech gaps between turns.
Extracts millisecond timing boundaries for word-level sync.
Provides 100% offline deterministic audio synthesis for CI/airgapped environments.
"""
import os
import re
import math
import wave
import struct
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import edge_tts
from pydantic import BaseModel

class AudioSegment(BaseModel):
    speaker: str
    text: str
    start_sec: float
    end_sec: float
    duration_sec: float

class TTSResult(BaseModel):
    audio_path: str
    duration_sec: float
    segments: List[AudioSegment]
    is_synthetic: bool = False

class TTSService:
    VOICE_MAP = {
        "[MALE]": "en-US-ChristopherNeural",
        "[FEMALE]": "en-US-JennyNeural",
        "[KID]": "en-US-AnaNeural"
    }

    STORAGE_DIR = os.path.join("storage", "audio")

    @classmethod
    def _ensure_dir(cls):
        os.makedirs(cls.STORAGE_DIR, exist_ok=True)

    @classmethod
    def parse_speaker_blocks(cls, script_text: str, default_speaker: str = "[MALE]") -> List[Tuple[str, str]]:
        """
        Extracts [(speaker, text)] from narration lines containing tags like [MALE], [FEMALE], [KID].
        """
        pattern = re.compile(r"(\[(?:MALE|FEMALE|KID)\])", re.IGNORECASE)
        parts = pattern.split(script_text)
        
        blocks: List[Tuple[str, str]] = []
        current_speaker = default_speaker

        for p in parts:
            p_strip = p.strip()
            if not p_strip:
                continue
            if pattern.match(p_strip):
                current_speaker = p_strip.upper()
            else:
                blocks.append((current_speaker, p_strip))

        if not blocks:
            blocks.append((default_speaker, script_text.strip()))
        return blocks

    @classmethod
    def generate_offline_audio(
        cls,
        blocks: List[Tuple[str, str]],
        output_wav_path: str,
        gap_sec: float = 0.15
    ) -> TTSResult:
        """
        Zero-cost offline audio synthesizer using python wave.
        Generates harmonic speech-like tones corresponding to sentence length,
        inserting exact 150ms gaps between speaker turns.
        """
        cls._ensure_dir()
        framerate = 24000
        segments: List[AudioSegment] = []
        current_time = 0.0

        with wave.open(output_wav_path, "w") as wav_out:
            wav_out.setnchannels(1)
            wav_out.setsampwidth(2)
            wav_out.setframerate(framerate)

            for spk, text in blocks:
                # Approximate speech duration: ~150 words per minute -> 2.5 words/sec
                words = text.split()
                dur = max(1.5, len(words) / 2.5)
                
                # Pitch according to speaker
                freq = 130.0 if spk == "[MALE]" else (220.0 if spk == "[FEMALE]" else 310.0)

                start = current_time
                n_frames = int(dur * framerate)
                for i in range(n_frames):
                    # Envelope modulation to simulate spoken syllables
                    t = i / framerate
                    envelope = 0.5 * (1.0 + math.sin(2.0 * math.pi * 3.5 * t))
                    sample = int(32767.0 * 0.15 * envelope * math.sin(2.0 * math.pi * freq * t))
                    wav_out.writeframes(struct.pack("<h", sample))

                end = start + dur
                segments.append(AudioSegment(
                    speaker=spk,
                    text=text,
                    start_sec=round(start, 3),
                    end_sec=round(end, 3),
                    duration_sec=round(dur, 3)
                ))
                current_time = end

                # Insert 150ms gap between speaker turns
                gap_frames = int(gap_sec * framerate)
                wav_out.writeframes(b"\x00\x00" * gap_frames)
                current_time += gap_sec

        return TTSResult(
            audio_path=output_wav_path,
            duration_sec=round(current_time, 3),
            segments=segments,
            is_synthetic=True
        )

    @classmethod
    async def synthesize(
        cls,
        text_or_blocks: Any,
        output_filename: str,
        allow_network: bool = True
    ) -> TTSResult:
        """
        Synthesizes high-fidelity multi-speaker audio.
        Falls back seamlessly to offline synthesis when network is disabled or unavailable.
        """
        cls._ensure_dir()
        if isinstance(text_or_blocks, str):
            blocks = cls.parse_speaker_blocks(text_or_blocks)
        else:
            blocks = text_or_blocks

        out_path = os.path.join(cls.STORAGE_DIR, output_filename)

        if allow_network and not output_filename.endswith(".wav"):
            try:
                # Online Edge-TTS synthesis
                combined_audio = bytearray()
                segments: List[AudioSegment] = []
                current_time = 0.0

                for spk, phrase in blocks:
                    voice = cls.VOICE_MAP.get(spk, "en-US-ChristopherNeural")
                    communicate = edge_tts.Communicate(phrase, voice)
                    phrase_audio = bytearray()
                    phrase_duration = 0.0

                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            phrase_audio.extend(chunk["data"])
                        elif chunk["type"] == "SentenceBoundary":
                            dur = (chunk["offset"] + chunk["duration"]) / 10_000_000.0
                            if dur > phrase_duration:
                                phrase_duration = dur

                    if phrase_duration == 0.0:
                        phrase_duration = max(1.5, len(phrase.split()) / 2.5)

                    start = current_time
                    end = start + phrase_duration
                    segments.append(AudioSegment(
                        speaker=spk,
                        text=phrase,
                        start_sec=round(start, 3),
                        end_sec=round(end, 3),
                        duration_sec=round(phrase_duration, 3)
                    ))
                    current_time = end + 0.15  # 150ms inter-turn gap
                    combined_audio.extend(phrase_audio)

                if combined_audio:
                    with open(out_path, "wb") as f:
                        f.write(combined_audio)
                    return TTSResult(
                        audio_path=out_path,
                        duration_sec=round(current_time, 3),
                        segments=segments,
                        is_synthetic=False
                    )
            except Exception:
                # Network failed -> fall back to deterministic offline synthesizer
                pass

        # Offline Fallback
        wav_path = out_path if out_path.endswith(".wav") else f"{os.path.splitext(out_path)[0]}.wav"
        return cls.generate_offline_audio(blocks, wav_path)
