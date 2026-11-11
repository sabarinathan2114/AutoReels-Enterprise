import os
import subprocess
import imageio_ffmpeg
from typing import List, Dict, Any, Optional

class RenderService:
    @staticmethod
    def get_ffmpeg_binary() -> str:
        return imageio_ffmpeg.get_ffmpeg_exe()

    @staticmethod
    def render_reel(
        scene_image_paths: List[str],
        audio_path: str,
        srt_path: Optional[str] = None,
        output_filename: str = "final_reel.mp4",
        fps: int = 30,
        resolution: str = "720x1280",
        watermark: bool = False
    ) -> str:
        """
        AutoReels v2.0 Compositing Engine:
        Stitches scene visuals with speech audio into 9:16 vertical video.
        Supports Ken Burns scale/crop and optional brand watermark.
        """
        ffmpeg_exe = RenderService.get_ffmpeg_binary()
        
        # Absolute storage path resolution
        storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "storage"))
        output_dir = os.path.join(storage_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        final_mp4_path = os.path.join(output_dir, output_filename)
        
        # Calculate duration of audio using ffprobe/ffmpeg
        abs_audio_path = os.path.abspath(audio_path)
        probe_cmd = [ffmpeg_exe, "-i", abs_audio_path]
        probe_res = subprocess.run(probe_cmd, stderr=subprocess.PIPE, text=True)
        
        duration = 15.0  # default fallback
        for line in probe_res.stderr.splitlines():
            if "Duration" in line:
                try:
                    time_part = line.split("Duration:")[1].split(",")[0].strip()
                    h, m, s = time_part.split(":")
                    duration = float(h) * 3600 + float(m) * 60 + float(s)
                except Exception:
                    pass
                break

        # Calculate duration per scene
        valid_images = [img for img in scene_image_paths if os.path.exists(img)]
        if not valid_images:
            # Fallback: create a solid color 9:16 frame if no images exist
            fallback_img = os.path.join(storage_dir, "images", "autobackground.jpg")
            if not os.path.exists(fallback_img):
                from PIL import Image
                im = Image.new("RGB", (720, 1280), (15, 10, 28))
                im.save(fallback_img)
            valid_images = [fallback_img]

        duration_per_scene = max(duration / len(valid_images), 2.0)
        
        # Build concat list file
        concat_txt_path = os.path.join(output_dir, "concat_list.txt")
        with open(concat_txt_path, "w", encoding="utf-8") as f:
            for img in valid_images:
                clean_img_path = os.path.abspath(img).replace("\\", "/")
                f.write(f"file '{clean_img_path}'\n")
                f.write(f"duration {duration_per_scene:.2f}\n")
            # Repeat last file to satisfy ffmpeg concat demuxer
            clean_last = os.path.abspath(valid_images[-1]).replace("\\", "/")
            f.write(f"file '{clean_last}'\n")

        width, height = resolution.split("x")
        
        # Build video filter chain (Scaling + Optional Watermark)
        vf_chain = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"
        if watermark:
            vf_chain += ",drawtext=text='AutoReels Free':x=w-tw-30:y=30:fontsize=24:fontcolor=white@0.7:box=1:boxcolor=black@0.5:boxborderw=5"
        
        cmd = [
            ffmpeg_exe,
            "-f", "concat",
            "-safe", "0",
            "-i", concat_txt_path,
            "-i", abs_audio_path,
            "-vf", vf_chain,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-y",
            os.path.abspath(final_mp4_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"FFmpeg render error: {result.stderr[-500:]}")

        return final_mp4_path
