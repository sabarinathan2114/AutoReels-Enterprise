# AutoReels Enterprise v2.0 — Verified Provider Facts & Limits

Updated: November 11, 2026

## 1. Pexels Stock Video & Photo API
- **Endpoint:** `https://api.pexels.com/v1/search`, `https://api.pexels.com/videos/search`
- **Rate Limit:** 200 requests/hour, 20,000 requests/month (Free Tier)
- **Aspect Ratio Filter:** `orientation=portrait` (guarantees vertical 9:16 content)
- **Source:** https://www.pexels.com/api/documentation/

## 2. Pollinations Flux AI Generation
- **Endpoint:** `https://image.pollinations.ai/prompt/{prompt}`
- **Dimensions:** `width=720&height=1280` (Free), `width=1080&height=1920` (Plan A/B/C)
- **Rate Limit:** Unmetered open community endpoint with exponential backoff on 429.
- **Source:** https://pollinations.ai/

## 3. Microsoft Edge-TTS
- **Voices Available:** >300 neural voices across 80+ locales including English, Tamil, Spanish, Hindi.
- **Output Formats:** `audio-24khz-48kbitrate-mono-mp3`
- **Word Timings:** Native subtitle tags with millisecond offset offsets.
