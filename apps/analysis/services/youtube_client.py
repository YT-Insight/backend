import re
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Patterns for the four URL formats YouTube supports
_CHANNEL_ID_RE = re.compile(r"youtube\.com/channel/([^/?&\s]+)")
_HANDLE_RE = re.compile(r"youtube\.com/@([^/?&\s]+)")
_CUSTOM_OR_USER_RE = re.compile(r"youtube\.com/(?:c/|user/)([^/?&\s]+)")


class YouTubeAPIError(Exception):
    """Raised when the YouTube Data API returns an unexpected error."""


class YouTubeClient:
    def __init__(self, api_key: str):
        self._youtube = build("youtube", "v3", developerKey=api_key)

    # ── Public interface ───────────────────────────────────────────────────

    def resolve_channel_id(self, channel_url: str) -> str:
        """Return the canonical channel ID (UCxxxxx) for any YouTube channel URL."""
        match = _CHANNEL_ID_RE.search(channel_url)
        if match:
            return match.group(1)

        match = _HANDLE_RE.search(channel_url)
        if match:
            return self._id_from_handle(match.group(1))

        match = _CUSTOM_OR_USER_RE.search(channel_url)
        if match:
            return self._id_from_search(match.group(1))

        raise YouTubeAPIError(f"Unrecognised YouTube channel URL: {channel_url!r}")

    def get_channel_info(self, channel_id: str) -> dict:
        """Return channel metadata as a dict ready for Channel model creation."""
        try:
            response = self._youtube.channels().list(
                part="snippet,statistics",
                id=channel_id,
            ).execute()
        except HttpError as exc:
            raise YouTubeAPIError(f"YouTube API error fetching channel {channel_id}: {exc}") from exc

        items = response.get("items", [])
        if not items:
            raise YouTubeAPIError(f"Channel not found: {channel_id}")

        item = items[0]
        snippet = item["snippet"]
        stats = item.get("statistics", {})

        return {
            "youtube_channel_id": channel_id,
            "title": snippet["title"],
            "description": snippet.get("description", ""),
            "thumbnail_url": self._best_thumbnail(snippet.get("thumbnails", {})),
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
        }

    def get_channel_videos(self, channel_id: str, max_results: int = 20) -> list[dict]:
        """Return up to `max_results` recent videos with stats for a channel."""
        playlist_id = self._uploads_playlist_id(channel_id)
        video_ids = self._video_ids_from_playlist(playlist_id, max_results)
        if not video_ids:
            return []
        return self._video_details(video_ids)

    def get_video_comments(self, video_id: str, max_results: int = 300) -> list[dict]:
        """Return up to `max_results` top-level comments for a video.

        Returns an empty list when comments are disabled rather than raising.
        """
        comments: list[dict] = []
        next_page_token = None

        while len(comments) < max_results:
            batch = min(100, max_results - len(comments))
            try:
                response = self._youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=batch,
                    pageToken=next_page_token,
                    textFormat="plainText",
                    order="relevance",
                ).execute()
            except HttpError as exc:
                if exc.resp.status == 403:
                    # Comments disabled for this video — not an error, just skip
                    logger.info("Comments disabled for video %s", video_id)
                    break
                raise YouTubeAPIError(
                    f"YouTube API error fetching comments for {video_id}: {exc}"
                ) from exc

            for item in response.get("items", []):
                top = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "text": top.get("textDisplay", ""),
                    "author": top.get("authorDisplayName", ""),
                    "like_count": top.get("likeCount", 0),
                    "published_at": top.get("publishedAt"),
                })

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return comments

    # ── Private helpers ────────────────────────────────────────────────────

    def _id_from_handle(self, handle: str) -> str:
        try:
            response = self._youtube.channels().list(
                part="id",
                forHandle=handle,
            ).execute()
        except HttpError as exc:
            raise YouTubeAPIError(f"YouTube API error resolving handle @{handle}: {exc}") from exc

        items = response.get("items", [])
        if not items:
            raise YouTubeAPIError(f"No channel found for handle: @{handle}")
        return items[0]["id"]

    def _id_from_search(self, query: str) -> str:
        try:
            response = self._youtube.search().list(
                part="snippet",
                q=query,
                type="channel",
                maxResults=1,
            ).execute()
        except HttpError as exc:
            raise YouTubeAPIError(f"YouTube API error searching for channel {query!r}: {exc}") from exc

        items = response.get("items", [])
        if not items:
            raise YouTubeAPIError(f"No channel found matching: {query!r}")
        return items[0]["id"]["channelId"]

    def _uploads_playlist_id(self, channel_id: str) -> str:
        try:
            response = self._youtube.channels().list(
                part="contentDetails",
                id=channel_id,
            ).execute()
        except HttpError as exc:
            raise YouTubeAPIError(f"YouTube API error fetching playlist for {channel_id}: {exc}") from exc

        items = response.get("items", [])
        if not items:
            raise YouTubeAPIError(f"Channel not found: {channel_id}")
        return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def _video_ids_from_playlist(self, playlist_id: str, max_results: int) -> list[str]:
        ids: list[str] = []
        next_page_token = None

        while len(ids) < max_results:
            batch = min(50, max_results - len(ids))
            try:
                response = self._youtube.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id,
                    maxResults=batch,
                    pageToken=next_page_token,
                ).execute()
            except HttpError as exc:
                raise YouTubeAPIError(f"YouTube API error fetching playlist items: {exc}") from exc

            for item in response.get("items", []):
                vid = item["snippet"]["resourceId"].get("videoId")
                if vid:
                    ids.append(vid)

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return ids

    def _video_details(self, video_ids: list[str]) -> list[dict]:
        # The API accepts up to 50 IDs per request
        results: list[dict] = []

        for chunk_start in range(0, len(video_ids), 50):
            chunk = video_ids[chunk_start : chunk_start + 50]
            try:
                response = self._youtube.videos().list(
                    part="snippet,statistics",
                    id=",".join(chunk),
                ).execute()
            except HttpError as exc:
                raise YouTubeAPIError(f"YouTube API error fetching video details: {exc}") from exc

            for item in response.get("items", []):
                snippet = item["snippet"]
                stats = item.get("statistics", {})
                results.append({
                    "youtube_video_id": item["id"],
                    "title": snippet["title"],
                    "view_count": int(stats["viewCount"]) if stats.get("viewCount") else None,
                    "like_count": int(stats["likeCount"]) if stats.get("likeCount") else None,
                    "comment_count": int(stats["commentCount"]) if stats.get("commentCount") else None,
                    "published_at": snippet.get("publishedAt"),
                    "thumbnail_url": self._best_thumbnail(snippet.get("thumbnails", {})),
                })

        return results

    @staticmethod
    def _best_thumbnail(thumbnails: dict) -> str:
        for quality in ("maxres", "standard", "high", "medium", "default"):
            if quality in thumbnails:
                return thumbnails[quality].get("url", "")
        return ""
