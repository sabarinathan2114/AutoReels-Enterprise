from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import os

class BaseSocialAdapter(ABC):
    """
    Abstract Base Adapter for Social Media Publishing.
    Every platform (YouTube, Instagram, Facebook, TikTok, etc.)
    implements these standard methods.
    """
    def __init__(self, account_id: str, account_name: str, credentials: Dict[str, Any]):
        self.account_id = account_id
        self.account_name = account_name
        self.credentials = credentials

    @abstractmethod
    def validate_connection(self) -> bool:
        """Checks if tokens/credentials are active."""
        pass

    @abstractmethod
    def publish_video(self, video_path: str, title: str, description: str, tags: List[str]) -> Dict[str, Any]:
        """Uploads video to platform endpoint."""
        pass


class YouTubeShortsAdapter(BaseSocialAdapter):
    """
    YouTube Data API v3 Adapter for publishing YouTube Shorts.
    - Uses OAuth 2.0 (access_token + refresh_token).
    - Uploads video with 9:16 aspect ratio and tag #Shorts.
    """
    def validate_connection(self) -> bool:
        return bool(self.credentials.get("refresh_token"))

    def publish_video(self, video_path: str, title: str, description: str, tags: List[str]) -> Dict[str, Any]:
        # Formulate YouTube Shorts metadata
        shorts_title = f"{title} #Shorts" if "#Shorts" not in title else title
        full_desc = f"{description}\n\n{' '.join(tags)}\n#Shorts"
        
        # When Google API client is authenticated:
        # response = youtube.videos().insert(
        #     part="snippet,status",
        #     body={
        #         "snippet": {
        #             "title": shorts_title,
        #             "description": full_desc,
        #             "tags": tags,
        #             "categoryId": "22"
        #         },
        #         "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        #     },
        #     media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
        # ).execute()
        return {
            "platform": "youtube_shorts",
            "account": self.account_name,
            "status": "ready_to_broadcast",
            "title": shorts_title,
            "file": video_path,
            "endpoint": "https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status"
        }


class InstagramReelsAdapter(BaseSocialAdapter):
    """
    Meta Graph API Adapter for Instagram Reels.
    - Two-step asynchronous publishing:
      1. POST /{ig_user_id}/media with video_url and media_type=REELS
      2. Poll container status until FINISHED
      3. POST /{ig_user_id}/media_publish
    """
    def validate_connection(self) -> bool:
        return bool(self.credentials.get("access_token") and self.credentials.get("ig_user_id"))

    def publish_video(self, video_path: str, title: str, description: str, tags: List[str]) -> Dict[str, Any]:
        caption = f"{title}\n\n{description}\n\n{' '.join(tags)}"
        return {
            "platform": "instagram_reels",
            "account": self.account_name,
            "status": "ready_to_broadcast",
            "caption": caption,
            "file": video_path,
            "endpoint": f"https://graph.facebook.com/v19.0/{self.credentials.get('ig_user_id', 'me')}/media"
        }


class FacebookReelsAdapter(BaseSocialAdapter):
    """
    Meta Graph API Adapter for Facebook Page Reels.
    - Uses /{page_id}/video_reels endpoint with resumable chunked upload.
    """
    def validate_connection(self) -> bool:
        return bool(self.credentials.get("page_access_token"))

    def publish_video(self, video_path: str, title: str, description: str, tags: List[str]) -> Dict[str, Any]:
        return {
            "platform": "facebook_reels",
            "account": self.account_name,
            "status": "ready_to_broadcast",
            "file": video_path,
            "endpoint": f"https://graph.facebook.com/v19.0/{self.credentials.get('page_id')}/video_reels"
        }


class TikTokAdapter(BaseSocialAdapter):
    """
    TikTok Content Posting API Adapter.
    - Uses /v2/post/publish/video/init/ endpoint.
    """
    def validate_connection(self) -> bool:
        return bool(self.credentials.get("access_token"))

    def publish_video(self, video_path: str, title: str, description: str, tags: List[str]) -> Dict[str, Any]:
        return {
            "platform": "tiktok",
            "account": self.account_name,
            "status": "ready_to_broadcast",
            "file": video_path,
            "endpoint": "https://open.tiktokapis.com/v2/post/publish/video/init/"
        }


class SocialDispatcher:
    """
    Unified manager for handling multi-account broadcast distribution.
    """
    def __init__(self):
        self.accounts: Dict[str, BaseSocialAdapter] = {}
        self._load_registered_accounts()

    def _load_registered_accounts(self):
        # Demo starter profiles
        self.accounts["yt_shorts_main"] = YouTubeShortsAdapter(
            account_id="yt_1",
            account_name="Tech & Stories Shorts",
            credentials={"refresh_token": "mock_token"}
        )
        self.accounts["ig_reels_kids"] = InstagramReelsAdapter(
            account_id="ig_1",
            account_name="@ChuttiKuzhandhai_Official",
            credentials={"access_token": "mock_token", "ig_user_id": "17841400000000"}
        )
        self.accounts["fb_page_main"] = FacebookReelsAdapter(
            account_id="fb_1",
            account_name="Global Insights Page",
            credentials={"page_access_token": "mock_token", "page_id": "100200300"}
        )

    def get_connected_accounts(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": k,
                "name": v.account_name,
                "platform": v.__class__.__name__.replace("Adapter", ""),
                "is_connected": v.validate_connection()
            }
            for k, v in self.accounts.items()
        ]

    def broadcast_to_selected_accounts(
        self,
        account_ids: List[str],
        video_path: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> List[Dict[str, Any]]:
        results = []
        for aid in account_ids:
            if aid in self.accounts:
                adapter = self.accounts[aid]
                res = adapter.publish_video(video_path, title, description, tags)
                results.append(res)
        return results
