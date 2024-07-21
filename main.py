from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from youtube_utils import create_youtube_client, get_latest_videos
from summarizer import summarize_youtube_transcript
from dotenv import load_dotenv
import os

from markdown import markdown

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Serve static files like CSS, JS if needed
app.mount("/static", StaticFiles(directory="static"), name="static")


def fetch_and_summarize_videos(channel_id: str, timeframe_hours: int):
    """
    Fetches the latest videos from a YouTube channel and summarizes them.

    Args:
        channel_id (str): The ID of the YouTube channel.
        timeframe_hours (int): The number of hours to look back for new videos.

    Returns:
        str: A combined summary of the latest videos.
    """
    # Retrieve API keys from environment variables
    api_key = os.getenv("YOUTUBE_API_KEY")
    api_key_llm = os.getenv("OPENAI_API_KEY")

    if not api_key or not api_key_llm:
        raise HTTPException(
            status_code=500, detail="API keys are not set in environment variables."
        )

    # Create YouTube API client
    youtube_client = create_youtube_client()

    # Get the latest videos
    latest_videos = get_latest_videos(
        youtube_client, channel_id, hours=timeframe_hours, max_results=5
    )

    if not latest_videos:
        raise HTTPException(
            status_code=404, detail="No videos found or an error occurred."
        )

    # Store individual summaries
    individual_summaries = []

    # Process each video
    for video in latest_videos:
        video_url = video["url"]
        summary = summarize_youtube_transcript(video_url)
        individual_summaries.append(summary)

    # Combine individual summaries into a final summary
    return "\n\n".join(individual_summaries)


@app.get("/", response_class=HTMLResponse)
async def index():
    """
    Serve the HTML form for input.
    """
    with open("templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/summarize-videos/", response_class=JSONResponse)
async def summarize_youtube_videos_json(
    channel_id: str,
    timeframe_hours: int = Query(24, description="Timeframe in hours to look back"),
):
    """
    Endpoint to get a summary of the latest videos from a YouTube channel in JSON format.

    Args:
        channel_id (str): The ID of the YouTube channel.
        timeframe_hours (int): The number of hours to look back for new videos.

    Returns:
        dict: A dictionary containing the summarized text.
    """
    combined_summary = fetch_and_summarize_videos(channel_id, timeframe_hours)
    return {"summary": combined_summary}


@app.get("/summarize-videos/", response_class=HTMLResponse)
async def summarize_youtube_videos_html(
    channel_id: str,
    timeframe_hours: int = Query(24, description="Timeframe in hours to look back"),
):
    """
    Endpoint to get a summary of the latest videos from a YouTube channel in HTML format.

    Args:
        channel_id (str): The ID of the YouTube channel.
        timeframe_hours (int): The number of hours to look back for new videos.

    Returns:
        HTMLResponse: An HTML page displaying the summary.
    """
    combined_summary = fetch_and_summarize_videos(channel_id, timeframe_hours)

    # Convert Markdown summary to HTML
    html_summary = markdown(combined_summary)

    # Load and render HTML template
    with open("templates/summary.html", "r") as f:
        html_template = f.read()

    # Inject summary into the HTML template
    html_content = html_template.format(summary=combined_summary)

    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
