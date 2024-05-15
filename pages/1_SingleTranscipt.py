import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi as yta
import re

def extract_video_id(youtube_url):
    """
    Extracts the video ID from a YouTube URL.
    """
    if "youtube.com/watch" not in youtube_url:
        st.error("Invalid YouTube URL")
        return None
    index_v = youtube_url.find('v=')
    if index_v == -1:
        
        st.error("Video ID not found in the URL")
        return None
    video_id_start = index_v + 2
    video_id_end = youtube_url.find('&', video_id_start)
    video_id = youtube_url[video_id_start:video_id_end] if video_id_end != -1 else youtube_url[video_id_start:]
    return video_id

def transcribe_video(youtube_url):
    """
    Fetches and cleans the transcription of a given YouTube video.
    """
    video_id = extract_video_id(youtube_url)
    if video_id is None:
        return "Invalid YouTube URL"
    try:
        transcript = yta.get_transcript(video_id, languages=('us', 'en'))
        data1 = [t['text'] for t in transcript]
        data2 = [re.sub(r"[^a-zA-Z0-9-1sg��çiISGÖÜçï ]", "", line) for line in data1]
        return "\n".join(data2)
    except Exception as e:
        return str(e)

# Streamlit interface
st.title("YouTube Video Transcription Extractor")
youtube_url = st.text_input("Enter the YouTube Video URL", placeholder="Example: https://www.youtube.com/watch?v=MnDudvCyWpc")
if youtube_url:
    video_id = extract_video_id(youtube_url)
    if video_id:
        video_embed_url = f"https://www.youtube.com/embed/{video_id}"
        st.video(video_embed_url)

if st.button("Transcribe Video"):
    result = transcribe_video(youtube_url)
    st.text_area("Transcription:", value=result, height=300)
