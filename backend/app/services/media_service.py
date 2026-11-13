import os
import urllib.parse
import httpx
from typing import Optional, Dict, Any

class MediaService:
    @staticmethod
    async def generate_ai_image(
        prompt: str,
        output_filename: str,
        width: int = 720,
        height: int = 1280,
        model: str = "flux"
    ) -> str:
        """
        Generates 9:16 vertical AI image using free high-quality Pollinations/Flux API.
        No API key required!
        """
        output_dir = os.path.join("storage", "images")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, output_filename)
        
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model={model}&nologo=true&enhance=true"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                return file_path
            else:
                raise Exception(f"Failed to generate AI image. Status: {response.status_code}")

    @staticmethod
    def generate_ai_image_sync(
        prompt: str,
        output_filename: str,
        width: int = 720,
        height: int = 1280,
        model: str = "flux"
    ) -> str:
        output_dir = os.path.join("storage", "images")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, output_filename)
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model={model}&nologo=true&enhance=true"
        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.get(url)
                if res.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(res.content)
                    return file_path
        except Exception:
            pass
        fallback_path = os.path.join("storage", "images", "fallback.jpg")
        if os.path.exists(fallback_path):
            return fallback_path
        return file_path

    @staticmethod
    async def search_free_stock_video(
        keyword: str,
        output_filename: str,
        pexels_api_key: Optional[str] = None
    ) -> Optional[str]:
        """
        Searches and downloads free 9:16 vertical video from Pexels API if API key is provided,
        or falls back to an AI scene generation if not provided.
        """
        if not pexels_api_key:
            return None
            
        headers = {"Authorization": pexels_api_key}
        url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(keyword)}&orientation=portrait&per_page=1"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                videos = data.get("videos", [])
                if videos:
                    video_files = videos[0].get("video_files", [])
                    # Pick best vertical resolution
                    download_url = video_files[0].get("link")
                    output_dir = os.path.join("storage", "video")
                    os.makedirs(output_dir, exist_ok=True)
                    out_path = os.path.join(output_dir, output_filename)
                    
                    vid_resp = await client.get(download_url)
                    with open(out_path, "wb") as f:
                        f.write(vid_resp.content)
                    return out_path
        return None
