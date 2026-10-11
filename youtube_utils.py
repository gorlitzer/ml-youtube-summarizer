from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")


# Create a YouTube API client
def create_youtube_client():
    """Create a YouTube API client."""
    return build("youtube", "v3", developerKey=api_key)


def get_latest_videos(youtube_client, channel_id, hours=24, max_results=5):
    """
    Fetch the latest videos from a YouTube channel.

    Args:
        youtube_client: An instance of the YouTube API client.
        channel_id (str): The ID of the YouTube channel.
        hours (int): The number of hours to look back for new videos.
        max_results (int): The maximum number of results to return.

    Returns:
        list: A list of dictionaries containing video details.
    """
    published_after = (datetime.utcnow() - timedelta(hours=hours)).isoformat() + "Z"

    try:
        request = youtube_client.search().list(
            part="snippet",
            channelId=channel_id,
            order="date",
            maxResults=max_results,
            publishedAfter=published_after,
        )
        response = request.execute()

        videos = [
            {
                "title": item["snippet"]["title"],
                "video_id": item["id"]["videoId"],
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            }
            for item in response["items"]
        ]

        return videos
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


if __name__ == "__main__":
    # Load environment variables from .env file
    from dotenv import load_dotenv

    load_dotenv()

    # Retrieve API key and channel ID from environment variables
    api_key = os.getenv("YOUTUBE_API_KEY")
    channel_id = os.getenv("CHANNEL_ID")

    if not api_key or not channel_id:
        print("API key or Channel ID not found in environment variables.")
    else:
        # Create YouTube API client
        youtube_client = create_youtube_client(api_key)

        # Get latest videos
        latest_videos = get_latest_videos(
            youtube_client, channel_id, hours=24, max_results=5
        )
        for video in latest_videos:
            print(f"Title: {video['title']}")
            print(f"URL: {video['url']}")
            print()
