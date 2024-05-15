import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Streamlit user interface for API Key input
st.title('YouTube Channel Video Fetcher')
api_key = st.text_input('Enter your Google API Key:', type="password")

if api_key:
    # YouTube API setup
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    def get_videos_from_channel(channel_id):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=api_key)

        channel_response = youtube.channels().list(
            id=channel_id,
            part="contentDetails"
        ).execute()

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
                videos.append((video_title, f"https://www.youtube.com/watch?v={video_id}"))

            next_page_token = playlist_items_response.get("nextPageToken")
            if not next_page_token:
                break

        return videos

    channel_url = st.text_input('Enter YouTube channel URL:')
    if channel_url:
        try:
            # Extracting channel ID from the URL
            if 'channel/' in channel_url:
                channel_id = channel_url.split('channel/')[-1]
            else:
                st.error("Please enter a valid YouTube channel URL.")
                st.stop()

            videos = get_videos_from_channel(channel_id)

            if videos:
                st.write(f"Channel URL: {channel_url}")
                st.write("Videos in the channel:")
                for title, url in videos:
                    st.markdown(f"[{title}]({url})")
            else:
                st.write("No videos found in this channel.")
        except HttpError as e:
            st.error(f"An error occurred: {e}")
else:
    st.warning("Please enter a Google API Key to use this app.")
