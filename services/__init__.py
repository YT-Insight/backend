from googleapiclient.discovery import build
from django.conf import settings

class YouTubeService:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def get_video_details(self, video_id: str) -> dict:
        """Получает сырые данные от YouTube"""
        request = self.youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        )
        response = request.execute()
        # Тут может быть обработка ошибок
        return response['items'][0] if response['items'] else None

    def get_comments(self, video_id: str, max_results=50):
        # Логика получения комментов
        pass