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

    def youtube_search(query):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=api_key)

        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=25,
            type="channel",
            order="relevance"
        ).execute()

        channels = []
        for search_result in search_response.get("items", []):
            channel_title = search_result["snippet"]["title"]
            channel_id = search_result["id"]["channelId"]
            channel_url = f"https://www.youtube.com/channel/{channel_id}"
            channels.append((channel_title, channel_id, channel_url))
        return channels

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

    query = st.text_input('Enter a topic or company name to search for YouTube channels:')
    if query:
        try:
            channels = youtube_search(query)
            if channels:
                channel_options = {f"[{name}]({url})": id for name, id, url in channels}
                channel_name = st.selectbox('Select a channel:', list(channel_options.keys()))
                channel_id = channel_options[channel_name]
                videos = get_videos_from_channel(channel_id)

                if videos:
                    st.write(f"Channel URL: https://www.youtube.com/channel/{channel_id}")
                    st.write(f"Videos in {channel_name} channel:")
                    for title, url in videos:
                        st.markdown(f"[{title}]({url})")
                else:
                    st.write("No videos found in this channel.")
            else:
                st.write("No channels found.")
        except HttpError as e:
            st.error(f"An error occurred: {e}")
else:
    st.warning("Please enter a Google API Key to use this app.")
