"""
YouTube Data API v3 uploader — handles OAuth refresh, resumable upload,
thumbnail setting, and scheduled publishing.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]


class YouTubeUploader:
    def __init__(self, cfg):
        self.cfg = cfg
        self._service = None

    def _get_service(self):
        if self._service:
            return self._service

        creds = Credentials(
            token=None,
            refresh_token=self.cfg.YOUTUBE_REFRESH_TOKEN,
            client_id=self.cfg.YOUTUBE_CLIENT_ID,
            client_secret=self.cfg.YOUTUBE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=SCOPES,
        )
        creds.refresh(Request())
        self._service = build("youtube", "v3", credentials=creds)
        return self._service

    def upload(self, video_path: Path, thumbnail_path: Path, metadata: dict) -> str:
        """Upload video, set thumbnail, and return the video ID."""
        service = self._get_service()

        # Parse scheduled publish time
        publish_at = self._scheduled_time()

        body = {
            "snippet": {
                "title": metadata["title"],
                "description": metadata["description"],
                "tags": metadata.get("tags", []),
                "categoryId": self.cfg.VIDEO_CATEGORY_ID,
                "defaultLanguage": self.cfg.VIDEO_LANGUAGE,
            },
            "status": {
                "privacyStatus": "private",  # Will be public at publish_at
                "publishAt": publish_at,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
            chunksize=50 * 1024 * 1024,  # 50 MB chunks
        )

        logger.info(f"Uploading '{metadata['title']}' (scheduled: {publish_at})")
        request = service.videos().insert(part="snippet,status", body=body, media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                logger.info(f"Upload progress: {pct}%")

        video_id = response["id"]
        logger.info(f"Upload complete. Video ID: {video_id}")

        # Set thumbnail
        if thumbnail_path.exists():
            self._set_thumbnail(service, video_id, thumbnail_path)

        return video_id

    def _set_thumbnail(self, service, video_id: str, thumb_path: Path) -> None:
        media = MediaFileUpload(str(thumb_path), mimetype="image/jpeg")
        service.thumbnails().set(videoId=video_id, media_body=media).execute()
        logger.info(f"Thumbnail set for {video_id}")

    def _scheduled_time(self) -> str:
        """Return the next occurrence of the configured upload time as ISO 8601."""
        hour, minute = map(int, self.cfg.UPLOAD_TIME.split(":"))
        now = datetime.now(timezone.utc)
        scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if scheduled <= now:
            scheduled += timedelta(days=1)
        return scheduled.isoformat()
