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

    def get_videos_from_channel(channel_id=None, username=None):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key)
        
        # Get channel response based on channel_id or username
        if channel_id:
            channel_response = youtube.channels().list(id=channel_id, part="contentDetails").execute()
        elif username:
            channel_response = youtube.channels().list(forUsername=username, part="contentDetails").execute()
        else:
            return []
        
        # Check if the channel response contains any items
        if not channel_response.get("items"):
            st.error("No channel found. Please check the channel ID or username and try again.")
            st.stop()

        # Extract uploads playlist ID
        try:
            uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except (KeyError, IndexError) as e:
            st.error("This channel does not have an uploads playlist or the API response format has changed.")
            st.error(f"Error details: {e}")
            st.stop()

        # Retrieve videos from the uploads playlist
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
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                videos.append(video_url)

            next_page_token = playlist_items_response.get("nextPageToken")
            if not next_page_token:
                break

        return videos

    channel_url = st.text_input('Enter YouTube channel URL:')
    if channel_url:
        try:
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
                links_text = ", ".join(videos)
                edited_links = st.text_area("Edit video links:", links_text, height=300)
                st.write("Edited Links:", edited_links)
            else:
                st.write("No videos found in this channel.")
        except HttpError as e:
            st.error(f"An error occurred: {e}")
else:
    st.warning("Please enter a Google API Key to use this app.")
