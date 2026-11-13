"""
Visual Ladder Engine (Spec 4.1, 15.4)
Zero cash cost multi-tier visual provider with graceful degradation:
Tier 1: Free open Flux-schnell / Pollinations zero-cost model
Tier 2: Public domain stock image retrieval
Tier 3: Procedural Kinetic Typography Gradient Engine (Pillow, 100% offline reliable)
Includes Plan-tier watermark stamping.
"""
import os
import math
import random
import urllib.parse
from typing import Optional, Tuple
import httpx
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel

class VisualLadderResult(BaseModel):
    file_path: str
    provider: str
    degraded: bool
    width: int
    height: int

class VisualLadderService:
    STORAGE_DIR = os.path.join("storage", "images")

    @classmethod
    def _ensure_dir(cls):
        os.makedirs(cls.STORAGE_DIR, exist_ok=True)

    @classmethod
    def create_gradient_scene(
        cls,
        title_text: str,
        output_filename: str,
        scene_index: int = 0,
        width: int = 720,
        height: int = 1280
    ) -> str:
        """
        Tier 3: Procedural 9:16 vertical kinetic canvas with cosmic obsidian background,
        ambient violet/cyan glowing particle aura, and typography layout.
        Guaranteed to work 100% offline with zero network latency.
        """
        cls._ensure_dir()
        out_path = os.path.join(cls.STORAGE_DIR, output_filename)

        # Base obsidian canvas (#07040D to deep violet #1E0B36)
        im = Image.new("RGB", (width, height), color=(7, 4, 13))
        draw = ImageDraw.Draw(im)

        # Generate smooth vertical gradient
        top_color = (12, 6, 24)
        bottom_color = (28, 14, 52)
        for y in range(height):
            ratio = y / height
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Ambient cosmic glow circles
        glow_centers = [
            (int(width * 0.3), int(height * 0.25), 180, (139, 92, 246, 25)),
            (int(width * 0.7), int(height * 0.75), 220, (6, 182, 212, 20)),
            (int(width * 0.5), int(height * 0.5), 150, (192, 132, 252, 20)),
        ]
        
        # Draw soft concentric rings for cosmic aura
        for cx, cy, max_radius, col in glow_centers:
            for radius in range(max_radius, 0, -15):
                draw.ellipse(
                    [(cx - radius, cy - radius), (cx + radius, cy + radius)],
                    outline=(col[0], col[1], col[2])
                )

        # High-tech cyber frame
        margin = int(width * 0.06)
        draw.rounded_rectangle(
            [(margin, margin), (width - margin, height - margin)],
            radius=20,
            outline=(139, 92, 246),
            width=3
        )

        # Top Scene Badge
        badge_text = f"SCENE 0{scene_index + 1}"
        draw.rounded_rectangle(
            [(margin + 20, margin + 20), (margin + 160, margin + 60)],
            radius=8,
            fill=(26, 16, 48),
            outline=(192, 132, 252),
            width=2
        )
        draw.text((margin + 90, margin + 40), badge_text, fill=(245, 243, 255), anchor="mm")

        # Center typography card
        box_y1 = int(height * 0.38)
        box_y2 = int(height * 0.62)
        draw.rounded_rectangle(
            [(margin + 15, box_y1), (width - margin - 15, box_y2)],
            radius=16,
            fill=(18, 10, 36),
            outline=(168, 85, 247),
            width=2
        )

        # Formatted title text lines (wrap to 22 chars)
        clean_text = title_text.strip()
        words = clean_text.split()
        lines = []
        curr_line = []
        for w in words:
            curr_line.append(w)
            if len(" ".join(curr_line)) > 20:
                lines.append(" ".join(curr_line))
                curr_line = []
        if curr_line:
            lines.append(" ".join(curr_line))

        # Draw centered lines
        start_y = box_y1 + 40
        for idx, line in enumerate(lines[:4]):
            y_pos = start_y + (idx * 38)
            draw.text(
                (int(width / 2), y_pos),
                line,
                fill=(255, 255, 255),
                anchor="mm"
            )

        im.save(out_path, format="JPEG", quality=92)
        return out_path

    @classmethod
    async def generate_scene_visual(
        cls,
        prompt: str,
        output_filename: str,
        scene_index: int = 0,
        width: int = 720,
        height: int = 1280,
        allow_network: bool = True
    ) -> VisualLadderResult:
        """
        Executes the Image Ladder:
        1. Try Pollinations (Flux-schnell zero cost)
        2. Fallback to Kinetic Typography Gradient Engine
        """
        cls._ensure_dir()
        out_path = os.path.join(cls.STORAGE_DIR, output_filename)

        if allow_network:
            try:
                encoded_prompt = urllib.parse.quote(prompt[:200])
                url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model=flux&nologo=true"
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.get(url)
                    if resp.status_code == 200 and len(resp.content) > 1000:
                        with open(out_path, "wb") as f:
                            f.write(resp.content)
                        return VisualLadderResult(
                            file_path=out_path,
                            provider="pollinations_flux",
                            degraded=False,
                            width=width,
                            height=height
                        )
            except Exception:
                # Network failed or timed out -> cascade to Tier 3
                pass

        # Tier 3 Procedural Fallback
        fallback_path = cls.create_gradient_scene(
            title_text=prompt,
            output_filename=output_filename,
            scene_index=scene_index,
            width=width,
            height=height
        )

        return VisualLadderResult(
            file_path=fallback_path,
            provider="kinetic_typography_canvas",
            degraded=True,
            width=width,
            height=height
        )

    @classmethod
    def apply_watermark(
        cls,
        image_path: str,
        watermark_text: str = "⚡ AutoReels Free",
        output_path: Optional[str] = None
    ) -> str:
        """
        Stamps official AutoReels branding in bottom right corner for Free tier reels.
        """
        target_path = output_path or image_path
        with Image.open(image_path) as im:
            im = im.convert("RGBA")
            overlay = Image.new("RGBA", im.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)

            w, h = im.size
            # Watermark pill in bottom-right corner
            pill_w = 210
            pill_h = 44
            x1 = w - pill_w - 30
            y1 = h - pill_h - 60
            x2 = w - 30
            y2 = h - 60

            # Translucent dark pill background
            draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=12, fill=(15, 10, 25, 200), outline=(139, 92, 246, 240), width=2)
            draw.text((x1 + pill_w // 2, y1 + pill_h // 2), watermark_text, fill=(245, 243, 255, 255), anchor="mm")

            final_img = Image.alpha_composite(im, overlay).convert("RGB")
            final_img.save(target_path, format="JPEG", quality=92)

        return target_path
