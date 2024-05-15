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

def transcribe_videos(youtube_urls):
    """
    Fetches and cleans the transcriptions of given YouTube videos.
    """
    all_transcripts = []
    for url in youtube_urls.split(','):
        url = url.strip()
        video_id = extract_video_id(url)
        if video_id is None:
            continue
        try:
            transcript = yta.get_transcript(video_id, languages=('us', 'en'))
            cleaned_text = [re.sub(r"[^a-zA-Z0-9-1sgçiISGÖÜçï ]", "", t['text']) for t in transcript]
            all_transcripts.append("\n".join(cleaned_text))
        except Exception as e:
            all_transcripts.append(f"Failed to transcribe {url}: {str(e)}")
    return "\n\n---\n\n".join(all_transcripts)

# Streamlit interface
st.title("YouTube Multiple-Video Transcription Extractor")
youtube_urls = st.text_input("Enter YouTube Video URLs separated by commas", placeholder="Example: https://www.youtube.com/watch?v=MnDudvCyWpc")
if st.button("Transcribe Videos"):
    result = transcribe_videos(youtube_urls)
    st.text_area("Transcriptions:", value=result, height=300)
    st.download_button("Download Transcripts", data=result, file_name="transcripts.txt", mime="text/plain")
