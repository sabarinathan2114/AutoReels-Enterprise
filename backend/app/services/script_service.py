import json
import os
from typing import Dict, Any, List

class ScriptService:
    @staticmethod
    def generate_story_blueprint(
        topic: str,
        niche: str = "emotional_drama",
        language: str = "Tamil"
    ) -> Dict[str, Any]:
        """
        Creates a structured multi-scene viral video blueprint.
        Matches the formula from the reference reel:
        0-3s: Immediate Hook
        4-40s: Escalating drama / interesting fact scenes
        40-55s: Emotional or thoughtful payoff / CTA
        """
        if niche == "emotional_drama" and language == "Tamil":
            return {
                "title": f"{topic} - ஒரு உணர்ச்சிகரமான கதை",
                "language": "Tamil",
                "voice_id": "ta-IN-ValluvarNeural",
                "hook_0_3s": "இந்த ஒரு ஆசை அவனுடைய மொத்த வாழ்க்கையையும் இப்படி மாற்றிவிடும் என்று அவன் நினைக்கவே இல்லை...",
                "full_narration": "இந்த ஒரு ஆசை அவனுடைய மொத்த வாழ்க்கையையும் இப்படி மாற்றிவிடும் என்று அவன் நினைக்கவே இல்லை. "
                                  "தன் அம்மாவைக் காப்பாற்ற ஒரே ஒரு மந்திர ஆசையை அவன் பயன்படுத்தினான். "
                                  "ஆனால் அந்த ஆசை நிறைவேறும் தருணத்தில், அவன் வாழ்ந்த கிராமமே மிகப்பெரிய ஆபத்தில் மூழ்கியது. "
                                  "அவன் செய்த தியாகமும், அம்மாவின் பாசமும் இறுதியில் எதை வென்றது தெரியுமா? "
                                  "இந்த முடிவை உங்களால் நம்பவே முடியாது. முழு கதையை தெரிந்துகொள்ள இப்போது பின்தொடருங்கள்!",
                "scenes": [
                    {
                        "scene_id": 1,
                        "duration_sec": 4,
                        "visual_prompt": "3D Pixar style emotional Indian boy looking at a glowing magical token, cinematic lighting, cute expressive eyes, 8k vertical 9:16",
                        "stock_keyword": "emotional boy glowing magic",
                        "subtitles": "இந்த ஒரு ஆசை அவனுடைய வாழ்க்கையையே மாற்றியது..."
                    },
                    {
                        "scene_id": 2,
                        "duration_sec": 5,
                        "visual_prompt": "3D animated elderly Indian mother smiling weakly in a small rustic Indian cottage, warm soft golden hour light, heartwarming, 8k vertical 9:16",
                        "stock_keyword": "poor loving mother village cottage",
                        "subtitles": "தன் அம்மாவைக் காப்பாற்ற அந்த ஆசையை பயன்படுத்தினான்..."
                    },
                    {
                        "scene_id": 3,
                        "duration_sec": 5,
                        "visual_prompt": "Dramatic stormy clouds gathering over a peaceful vibrant Indian village with magical purple lightning, cinematic hyperrealistic, 8k vertical 9:16",
                        "stock_keyword": "dramatic stormy village lighting",
                        "subtitles": "ஆனால் கிராமமே மிகப்பெரிய ஆபத்தில் மூழ்கியது..."
                    },
                    {
                        "scene_id": 4,
                        "duration_sec": 4,
                        "visual_prompt": "Heartwarming embrace between mother and son with golden tears of joy and relief, magical aura, masterpiece, 8k vertical 9:16",
                        "stock_keyword": "mother and child emotional hug",
                        "subtitles": "அம்மாவின் பாசம் இறுதியில் வென்றது!"
                    }
                ],
                "recommended_hashtags": ["#TamilReels", "#AIStory", "#EmotionalStory", "#Shorts", "#ViralTamil"],
                "bgm_style": "emotional_flute_ambient"
            }
        else:
            # Default / English / Tech / Knowledge template
            return {
                "title": f"The Dark Truth About {topic}",
                "language": language,
                "voice_id": "en-US-ChristopherNeural",
                "hook_0_3s": f"Nobody is talking about what just happened with {topic}.",
                "full_narration": f"Nobody is talking about what just happened with {topic}. "
                                  "Behind closed doors, the biggest tech giants made a sudden shift that caught everyone off guard. "
                                  "What seemed like a routine update actually unlocks an entirely new automated future. "
                                  "If you're not paying attention to this right now, you might be left completely behind. "
                                  "Drop your thoughts below and subscribe for real daily updates.",
                "scenes": [
                    {
                        "scene_id": 1,
                        "duration_sec": 4,
                        "visual_prompt": "Futuristic neon data center with glowing purple server racks, cinematic cyberpunk aesthetic, 8k vertical 9:16",
                        "stock_keyword": "cyberpunk server room technology",
                        "subtitles": "Nobody is talking about this breakthrough..."
                    },
                    {
                        "scene_id": 2,
                        "duration_sec": 5,
                        "visual_prompt": "Futuristic humanoid robot hand interacting with a glowing violet neural hologram, 8k vertical 9:16",
                        "stock_keyword": "artificial intelligence neural network",
                        "subtitles": "A sudden shift that caught everyone off guard..."
                    },
                    {
                        "scene_id": 3,
                        "duration_sec": 5,
                        "visual_prompt": "High tech city skyline at night with flying drones and glowing purple neon lights, 8k vertical 9:16",
                        "stock_keyword": "futuristic smart city night",
                        "subtitles": "This unlocks an entirely new automated world..."
                    },
                    {
                        "scene_id": 4,
                        "duration_sec": 4,
                        "visual_prompt": "A modern creator studio with glowing purple ambient LEDs and ultra-wide screens, 8k vertical 9:16",
                        "stock_keyword": "modern studio glowing monitors",
                        "subtitles": "Subscribe to stay ahead of the future!"
                    }
                ],
                "recommended_hashtags": ["#TechShorts", "#AIRevolution", "#FutureTech", "#Shorts", "#Viral"],
                "bgm_style": "cyberpunk_synth_pulsing"
            }
