# AI Reels Studio & Multi-Account Social Dashboard

An autonomous, all-in-one short-form video creation studio and multi-channel publishing engine. Built with **Python FastAPI**, **Next.js 14/16 (App Router)**, **Tailwind CSS**, and **FFmpeg**.

Inspired by the dark obsidian & neon violet cosmic design language and the 100% free video production pipeline (Edge-TTS + Pollinations Flux AI + Pexels + local Whisper).

---

## 🚀 Quick Start (1-Click Run)

To run both the backend and frontend simultaneously on Windows, double-click:
```cmd
run_app.bat
```
Or start them manually in two terminals:

### 1. Start Python FastAPI Backend:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* Backend API: `http://localhost:8000`
* Interactive API Documentation (Swagger): `http://localhost:8000/docs`

### 2. Start Next.js Frontend:
```bash
cd frontend
npm run dev
```
* Web Studio UI: `http://localhost:3000`

---

## 🎨 Features & Capabilities

1. **All-in-One Studio Canvas**:
   * No hopping across multiple websites (ChatGPT, ElevenLabs, Midjourney, CapCut, YouTube, Instagram).
   * Script generation matching the viral short-form storytelling formula (Hook $\rightarrow$ Rising Drama $\rightarrow$ Payoff).
   * Free high-quality neural voiceover (Tamil `Valluvar/Pallavi`, English `Christopher/Guy`, Hindi `Madhur/Swara`).
   * Scene-by-scene 9:16 vertical AI image generation and stock video fetcher.
   * Dynamic kinetic typography (Alex Hormozi / MrBeast bouncing karaoke captions).
   * Live 9:16 interactive video player simulation.

2. **Multi-Account Social Media Dashboard**:
   * Manage multiple YouTube Shorts channels and Instagram Reels accounts under one roof.
   * One-click batch publishing to all selected destination accounts.
   * Extensible **Social Adapter Architecture** supporting YouTube Shorts, Instagram Reels, Facebook Reels, TikTok, and future platforms.

3. **100% Free Generation Pipeline**:
   * **Voice**: Microsoft Edge-TTS (No API key, zero cost, unlimited).
   * **Visuals**: Pollinations Flux.1 AI generation & Pexels API.
   * **Subtitles**: Millisecond word-level timing via Edge-TTS SubMaker / Whisper.
   * **Compositor**: Bundled FFmpeg binary via `imageio-ffmpeg`.
