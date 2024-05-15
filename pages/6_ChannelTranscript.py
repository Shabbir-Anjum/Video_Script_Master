import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi as yta
import re

# Helper functions for video processing and transcription
def extract_video_id(youtube_url):
    index_v = youtube_url.find('v=')
    if index_v == -1:
        return None
    video_id_start = index_v + 2
    video_id_end = youtube_url.find('&', video_id_start)
    return youtube_url[video_id_start:video_id_end] if video_id_end != -1 else youtube_url[video_id_start:]

def transcribe_videos(youtube_urls, videos):
    video_dict = {v[0]: v[1] for v in videos}
    all_transcripts = []
    for url in youtube_urls.split(','):
        url = url.strip()
        video_id = extract_video_id(url)
        video_name = video_dict.get(url, "Unknown Video")
        try:
            transcript = yta.get_transcript(video_id, languages=('us', 'en'))
            cleaned_text = [re.sub(r"[^a-zA-Z0-9-1sgçiISGÖÜçï ]", "", t['text']) for t in transcript]
            all_transcripts.append(f"{video_name}:\n" + "\n".join(cleaned_text))
        except Exception as e:
            all_transcripts.append(f"Failed to transcribe {url}: {str(e)}")
    return "\n\n---\n\n".join(all_transcripts)

# Streamlit user interface for API Key input
st.title('YouTube Channel Video Fetcher and Transcriber')
api_key = st.text_input('Enter your Google API Key:', type="password")

if api_key:
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    def get_videos_from_channel(channel_id=None, username=None):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key)
        if channel_id:
            channel_response = youtube.channels().list(id=channel_id, part="contentDetails").execute()
        elif username:
            channel_response = youtube.channels().list(forUsername=username, part="contentDetails").execute()
        else:
            return []

        if not channel_response.get("items"):
            st.error("No channel found. Please check the channel ID or username and try again.")
            return []

        uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        videos = []
        next_page_token = None
        while True:
            playlist_items_response = youtube.playlistItems().list(
                playlistId=uploads_playlist_id,
                part="snippet",
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            for item in playlist_items_response["items"]:
                video_id = item["snippet"]["resourceId"]["videoId"]
                video_title = item["snippet"]["title"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                videos.append((video_url, video_title))

            next_page_token = playlist_items_response.get("nextPageToken")
            if not next_page_token:
                break
        return videos

    channel_url = st.text_input('Enter YouTube channel URL:')
    if channel_url:
        if 'channel/' in channel_url:
            channel_id = channel_url.split('channel/')[-1]
            videos = get_videos_from_channel(channel_id=channel_id)
        elif '@' in channel_url:
            username = channel_url.split('@')[-1]
            videos = get_videos_from_channel(username=username)
        else:
            st.error("Please enter a valid YouTube channel URL.")
            st.stop()

        if videos:
            st.write(f"Channel URL: {channel_url}")
            st.write("Videos in the channel:")
            video_links_text = ", ".join([v[0] for v in videos])
            edited_links = st.text_area("Edit video links:", video_links_text, height=300)
            if st.button("Transcribe Videos"):
                transcriptions = transcribe_videos(edited_links, videos)
                st.text_area("Transcriptions:", value=transcriptions, height=300)
                st.download_button("Download Transcripts", data=transcriptions, file_name="transcripts.txt", mime="text/plain")
        else:
            st.write("No videos found in this channel.")
            
else:
    st.warning("Please enter a Google API Key to use this app.")

