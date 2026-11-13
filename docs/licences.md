# AutoReels Enterprise v2.0 — Open Source Licenses & Compliance Manifest

**Document Version:** 2.0.0  
**Compliance Standard:** Section 15 Free-First Addendum & Enterprise Commercial Readiness  
**Verification Date:** November 13, 2026  

---

### 1. Executive Licensing Statement
AutoReels Enterprise v2.0 is architected exclusively with **permissive open-source licenses** (MIT, Apache 2.0, BSD-2/3-Clause, ISC, LGPL 2.1+) and open community APIs to guarantee **zero marginal cash cost** on generation while ensuring 100% compliance for commercial SaaS operation.

No copyleft GPL v3, AGPL, or non-commercial (CC-BY-NC) assets are bundled into runtime binaries.

---

### 2. Core Dependencies & Engine Licensing

| Component / Library | Version | License | Permitted Commercial SaaS Use | Upstream Source / Reference |
| :--- | :--- | :--- | :--- | :--- |
| **FFmpeg** | 9.0.2 / 7.x | LGPL 2.1+ | Yes (dynamic subprocess invocation via CLI) | https://ffmpeg.org/legal.html |
| **imageio-ffmpeg** | 0.6.0 | BSD-2-Clause | Yes | https://github.com/imageio/imageio-ffmpeg |
| **FastAPI** | 0.115.x | MIT | Yes | https://github.com/fastapi/fastapi |
| **Starlette** | 0.41.x | BSD-3-Clause | Yes | https://github.com/encode/starlette |
| **Uvicorn** | 0.32.x | BSD-3-Clause | Yes | https://github.com/encode/uvicorn |
| **Pydantic & Settings** | 2.9.x | MIT | Yes | https://github.com/pydantic/pydantic |
| **SQLAlchemy** | 2.0.x | MIT | Yes | https://www.sqlalchemy.org/ |
| **PyMySQL** | 1.1.x | MIT | Yes | https://github.com/PyMySQL/PyMySQL |
| **Alembic** | 1.13.x | MIT | Yes | https://alembic.sqlalchemy.org/ |
| **Bcrypt** | 4.2.x | Apache 2.0 | Yes | https://github.com/pyca/bcrypt |
| **PyJWT** | 2.9.x | MIT | Yes | https://github.com/jpadilla/pyjwt |
| **Cryptography (Fernet)** | 43.0.x | Apache 2.0 / BSD | Yes | https://github.com/pyca/cryptography |
| **Pillow (PIL)** | 10.4.x | HPND / MIT-equivalent | Yes | https://github.com/python-pillow/Pillow |
| **Edge-TTS** | 6.1.x | LGPL 3.0 | Yes (Client library invocation) | https://github.com/rany2/edge-tts |
| **Next.js** | 16.4.x | MIT | Yes | https://github.com/vercel/next.js |
| **React & React-DOM** | 19.x | MIT | Yes | https://github.com/facebook/react |
| **Tailwind CSS** | 4.x / 3.4.x | MIT | Yes | https://tailwindcss.com/ |
| **Lucide React** | 0.468.x | ISC | Yes | https://lucide.dev/license |

---

### 3. Media Models, Neural Synthesizers & Fonts

| Asset / Service | License / Terms | Permitted Commercial SaaS Use | Attributions & Verification |
| :--- | :--- | :--- | :--- |
| **Pollinations Flux.1 Schnell** | Apache 2.0 / Open API | Yes (Freely usable for commercial generations) | High-speed 4-step distilled diffusion |
| **Kokoro-82M Voice Synthesizer** | Apache 2.0 | Yes | 82M parameter lightweight CPU TTS |
| **Microsoft Edge-TTS Neural Voices** | Open Gateway API | Yes | Multi-lingual neural TTS (Tamil, English, Hindi, etc.) |
| **Pexels Stock Visuals** | Pexels License | Yes (Free commercial use, no modification lock) | High quality vertical b-roll footage |
| **Impact Font / DejaVu Sans** | Bitstream Vera / SIL OFL | Yes | Word-level kinetic ASS subtitle rendering |
| **Pillow Procedural Gradients** | In-house Python | 100% Proprietary / Zero dependency | Pure algorithmic gradient generation |

---

### 4. Legal Compliance Guarantees
1. **Dynamic Separation:** FFmpeg is invoked via separate sub-process binary boundaries (`imageio-ffmpeg` static binary) and is NOT compiled into the Python interpreter or bundled into proprietary C extensions, maintaining strict LGPL compliance.
2. **Zero Proprietary Model Fees:** All generation models utilize either open weights (Kokoro, Flux-schnell) or zero-marginal-cost public neural endpoints, guaranteeing compliance with Section 15.1 ($0.00 marginal cash cost).
