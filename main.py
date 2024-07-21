from fastapi import FastAPI, HTTPException, Query
from langchain_openai import ChatOpenAI

from youtube_utils import create_youtube_client, get_latest_videos
from summarizer import summarize_youtube_transcript
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()


@app.get("/summarize-videos/")
async def summarize_youtube_videos(
    channel_id: str,
    timeframe_hours: int = Query(24, description="Timeframe in hours to look back"),
):
    """
    Endpoint to get a summary of the latest videos from a YouTube channel.

    Args:
        channel_id (str): The ID of the YouTube channel.
        timeframe_hours (int): The number of hours to look back for new videos.

    Returns:
        dict: A dictionary containing the summarized text.
    """
    # Retrieve API keys from environment variables
    api_key = os.getenv("YOUTUBE_API_KEY")
    api_key_llm = os.getenv("OPENAI_API_KEY")

    if not api_key or not api_key_llm:
        raise HTTPException(
            status_code=500, detail="API keys are not set in environment variables."
        )

    # Create YouTube API client
    youtube_client = create_youtube_client(api_key)

    # Get the latest videos
    latest_videos = get_latest_videos(
        youtube_client, channel_id, hours=timeframe_hours, max_results=5
    )

    if not latest_videos:
        raise HTTPException(
            status_code=404, detail="No videos found or an error occurred."
        )

    # Initialize LLM
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5, api_key=api_key_llm)

    # Store individual summaries
    individual_summaries = []

    # Process each video
    for video in latest_videos:
        video_url = video["url"]
        summary = summarize_youtube_transcript(video_url)
        individual_summaries.append(summary)

    # Combine individual summaries into a final summary
    combined_summary = "\n\n".join(individual_summaries)

    return {"summary": combined_summary}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
