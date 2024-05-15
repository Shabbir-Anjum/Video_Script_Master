import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi as yta
import re
import googleapiclient.discovery

# Initialize YouTube API client
def youtube_api_client(api_key):
    api_service_name = "youtube"
    api_version = "v3"
    return googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

def extract_channel_videos(channel_id, api_key):
    """
    Extracts all video IDs from a YouTube channel using the YouTube Data API.
    """
    youtube = youtube_api_client(api_key)
    video_ids = []
    next_page_token = None

    try:
        while True:
            request = youtube.search().list(
                part="id",
                channelId=channel_id,
                maxResults=50,  # You can fetch up to 50 results per request
                type="video",
                order="date",  # Newest videos first
                pageToken=next_page_token
            )
            response = request.execute()
            video_ids += [item['id']['videoId'] for item in response.get('items', [])]

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
    except Exception as e:
        st.error(f"Failed to fetch video IDs: {str(e)}")
        return []

    return video_ids

def transcribe_videos(video_ids):
    """
    Fetches and cleans the transcriptions of given YouTube videos.
    """
    all_transcripts = []
    for video_id in video_ids:
        try:
            transcript = yta.get_transcript(video_id, languages=('en',))
            cleaned_text = [re.sub(r"[^\w\s]", "", t['text']) for t in transcript]
            all_transcripts.append("\n".join(cleaned_text))
        except Exception as e:
            all_transcripts.append(f"Failed to transcribe video ID {video_id}: {str(e)}")
    return "\n\n---\n\n".join(all_transcripts)

# Streamlit interface
st.title("YouTube Channel Transcription Extractor")
api_key = st.text_input("Enter your Google API Key", type="password")
channel_id = st.text_input("Enter YouTube Channel ID", placeholder="Example: UCK8sQmJBp8GCxrOtXWBpyEA")
if st.button("Fetch Video List"):
    if api_key and channel_id:
        video_ids = extract_channel_videos(channel_id, api_key)
        video_ids_string = ", ".join(video_ids)
        edited_videos = st.text_area("Edit Video IDs (comma-separated):", value=video_ids_string, height=100)
        if st.button("Transcribe Edited Videos"):
            video_ids = edited_videos.split(',')
            result = transcribe_videos(video_ids)
            st.text_area("Transcriptions:", value=result, height=300)
            st.download_button("Download Transcripts", data=result, file_name="transcripts.txt", mime="text/plain")
    else:
        st.error("Please enter a valid Google API Key and YouTube Channel ID.")