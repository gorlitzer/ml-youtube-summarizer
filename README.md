# YouTube Channel Subscription Newsletter API

This Python API provides a summary of the latest videos from a specified YouTube channel. It integrates several tools to fetch video data, extract transcripts, and summarize the content using OpenAI's language models.

## Features

- Fetch the latest videos from a specified YouTube channel.
- Get detailed summaries of the video content.
- Easy integration with OpenAI’s GPT models for generating summaries.

## Project Structure

```bash
youtube_subscription_newsletter/
│
├── .envrc
├── .env
├── main.py
├── youtube_utils.py
├── summarizer.py
├── requirements.txt
└── README.md
```

- **`.envrc`**: Configuration file for `direnv` to set up the virtual environment and install dependencies.
- **`.env`**: Environment variables configuration file.
- **`main.py`**: FastAPI application and endpoint definition.
- **`youtube_utils.py`**: Contains functions for interacting with the YouTube API.
- **`summarizer.py`**: Contains functions for summarizing video transcripts.
- **`requirements.txt`**: Lists Python dependencies.
- **`README.md`**: This file.

## Environment Variables

Create a `.env` file in the root directory of the project with the following content:

```bash
YOUTUBE_API_KEY=your_youtube_api_key
OPENAI_API_KEY=your_openai_api_key
CHANNEL_ID=your_channel_id
TIMEFRAME_HOURS=24
```
