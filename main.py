import spotipy
from spotipy.oauth2 import SpotifyOAuth
from youtubesearchpython import VideosSearch
import yt_dlp
import os
from concurrent.futures import ThreadPoolExecutor, as_completed





# Get playlist details
def get_spotify_playlist(playlist_id):
    results = sp.playlist_items(playlist_id)
    tracks = results['items']
    song_names = [(track['track']['name'], track['track']['artists'][0]['name']) for track in tracks]
    return song_names

# Search for YouTube videos
def search_youtube(song):
    song_name = f"{song[0]} {song[1]}"
    videos_search = VideosSearch(song_name, limit=1)  
    results = videos_search.result()
    if results['result']:
        return song_name, results['result'][0]['link']
    return song_name, None

# Download audio from YouTube as MP3
def download_audio(song_info):
    song_name, youtube_url = song_info
    if youtube_url: 
        output_path = os.path.join('downloads', f"{song_name.replace('/', '')}.mp3")  
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return f"{song_name}.mp3 downloaded successfully!"
    return f"{song_name}: No valid URL found."

# Create the "downloads" directory if it doesn't exist
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# Example usage
playlist_id = input("ENTER YOUR PLAYLIST LINK:   \n")[34:]
playlist_id = playlist_id.split("?")[0]
songs = get_spotify_playlist(playlist_id)

# Use ThreadPoolExecutor for concurrent execution
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(search_youtube, song): song for song in songs}
    youtube_links = []

    for future in as_completed(futures):
        song_info = future.result()
        youtube_links.append(song_info)

    # Now download the audio concurrently
    download_futures = {executor.submit(download_audio, song_info): song_info for song_info in youtube_links}

    for future in as_completed(download_futures):
        print(future.result())

print("ALL SONGS ARE DOWNLOADED :))")

