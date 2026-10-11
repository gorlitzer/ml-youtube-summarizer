from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain import PromptTemplate
from langchain_openai import ChatOpenAI
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def summarize_youtube_transcript(youtube_url):
    # Load YouTube Video
    loader = YoutubeLoader.from_youtube_url(youtube_url, add_video_info=True)
    transcript = loader.load()

    # Splitting of YouTube Transcript into Chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=30)
    docs = text_splitter.split_documents(transcript)

    print(f"Number of Chunks: {len(docs)}")

    # Initialize LLM
    api_key = os.getenv(
        "OPENAI_API_KEY"
    )  # Update the environment variable name if necessary
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo", temperature=0.5, api_key=api_key, base_url=""
    )

    # Define the prompt template for the LLM
    prompt_template = """
    Please provide a summarized but comprehensive response 
    based on the following transcript of a youtube video:
    {input}

    Ensure the summary includes names of key companies, and relevant details like software and engines or library packages.
    """
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["input", youtube_url]
    )
    summarizing_chain = prompt | llm

    # Store the responses
    responses = []

    # Loop Begins here to fill above list of responses
    for i in range(len(docs)):
        response = summarizing_chain.invoke(input={"input": docs[i].page_content})
        if isinstance(response, dict):
            response = response.get("text", "")
        responses.append(response)
        time.sleep(0.5)  # Sleep to avoid hitting rate limits

    # Getting Overall Summary: Summary of Summaries
    summary_prompt_template = """
    Please provide a concise summary of the following responses for the video {youtube_url}:
    {responses}

    Include the title of the video at first and its url (not part of the list, but # Title). Followed by key details and names of companies mentioned. Ensure the final summary is concise and informative, like bullet points or short paragraphs.
    """
    summary_prompt = PromptTemplate(
        template=summary_prompt_template, input_variables=["responses", "youtube_url"]
    )
    summary_chain = summary_prompt | llm

    responses = [str(r) for r in responses]
    summary = summary_chain.invoke(
        input={"responses": "\n\n".join(responses), "youtube_url": youtube_url}
    )

    return summary.content


# Example usage
if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=D9V8LIJvZYE"
    summary = summarize_youtube_transcript(youtube_url)
    print(summary)
