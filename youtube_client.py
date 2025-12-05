from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config

class YouTubeClient:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=config.YOUTUBE_API_KEY)

    def search_channels(self, keyword, max_results=10):
        """
        Searches for channels matching the keyword.
        Returns a list of channel IDs.
        """
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=keyword,
                type="channel",
                maxResults=max_results
            )
            response = request.execute()
            
            channel_ids = [item['snippet']['channelId'] for item in response.get('items', [])]
            return channel_ids
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            return []

    def get_channel_details(self, channel_ids):
        """
        Fetches detailed information for a list of channel IDs.
        """
        if not channel_ids:
            return []
            
        try:
            request = self.youtube.channels().list(
                part="snippet,contentDetails,statistics,brandingSettings",
                id=','.join(channel_ids)
            )
            response = request.execute()
            return response.get('items', [])
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            return []

    def get_latest_video(self, channel_id):
        """
        Fetches the latest video for a channel.
        First tries to get the uploads playlist ID, then fetches the first item.
        """
        try:
            # 1. Get Uploads Playlist ID
            request = self.youtube.channels().list(
                part="contentDetails",
                id=channel_id
            )
            response = request.execute()
            items = response.get('items', [])
            if not items:
                return None
                
            uploads_playlist_id = items[0]['contentDetails']['relatedPlaylists']['uploads']
            
            # 2. Get latest video from playlist
            request = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=1
            )
            response = request.execute()
            items = response.get('items', [])
            if not items:
                return None
                
            return items[0]['snippet']
            
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            return None
