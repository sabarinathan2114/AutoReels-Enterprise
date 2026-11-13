import os
import asyncio
import edge_tts
from typing import List, Dict, Any

POPULAR_VOICES = [
    {
        "id": "ta-IN-ValluvarNeural",
        "name": "Valluvar (Tamil - Expressive Male)",
        "language": "Tamil",
        "gender": "Male"
    },
    {
        "id": "ta-IN-PallaviNeural",
        "name": "Pallavi (Tamil - Expressive Female)",
        "language": "Tamil",
        "gender": "Female"
    },
    {
        "id": "en-US-ChristopherNeural",
        "name": "Christopher (English - Storytelling Male)",
        "language": "English",
        "gender": "Male"
    },
    {
        "id": "en-US-GuyNeural",
        "name": "Guy (English - Energetic Male)",
        "language": "English",
        "gender": "Male"
    },
    {
        "id": "en-US-AriaNeural",
        "name": "Aria (English - Professional Female)",
        "language": "English",
        "gender": "Female"
    },
    {
        "id": "hi-IN-MadhurNeural",
        "name": "Madhur (Hindi - Dynamic Male)",
        "language": "Hindi",
        "gender": "Male"
    },
    {
        "id": "hi-IN-SwaraNeural",
        "name": "Swara (Hindi - Expressive Female)",
        "language": "Hindi",
        "gender": "Female"
    }
]

class VoiceService:
    @staticmethod
    def get_supported_voices() -> List[Dict[str, str]]:
        return POPULAR_VOICES

    @staticmethod
    async def generate_speech_with_subtitles(
        text: str,
        voice: str = "ta-IN-ValluvarNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        output_audio_path: str = "storage/audio/speech.mp3"
    ) -> Dict[str, Any]:
        """
        Synthesizes speech using free Edge-TTS and captures word-level / sentence boundaries.
        """
        os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        
        submaker = edge_tts.SubMaker()
        with open(output_audio_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.feed(chunk)
                    
        srt_content = submaker.get_srt()
        srt_path = output_audio_path.replace(".mp3", ".srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        return {
            "audio_path": output_audio_path,
            "srt_path": srt_path,
            "srt_content": srt_content,
            "voice": voice
        }

    @staticmethod
    def generate_speech_sync(
        text: str,
        voice: str = "ta-IN-ValluvarNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        output_audio_path: str = "storage/audio/speech.mp3"
    ) -> Dict[str, Any]:
        """Synchronous wrapper for Edge-TTS synthesis."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Inside already running loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(
                        asyncio.run,
                        VoiceService.generate_speech_with_subtitles(text, voice, rate, pitch, output_audio_path)
                    ).result()
        except Exception:
            pass
        return asyncio.run(
            VoiceService.generate_speech_with_subtitles(text, voice, rate, pitch, output_audio_path)
        )
