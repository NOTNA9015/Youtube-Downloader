#!/usr/bin/env python3

import os
from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
from tqdm import tqdm

def download_mp4(yt, output_path):
    stream = yt.streams.get_highest_resolution()
    print(f"Downloading video: {yt.title}")
    stream.download(output_path=output_path)
    print(f"✔ Downloaded: {yt.title}")

def download_mp3(yt, output_path):
    audio_stream = yt.streams.filter(only_audio=True).first()
    print(f"Downloading audio: {yt.title}")
    out_file = audio_stream.download(output_path=output_path)

    # Convert to MP3
    base, _ = os.path.splitext(out_file)
    mp3_file = base + ".mp3"
    os.system(f'ffmpeg -loglevel quiet -i "{out_file}" -vn -ab 192k -ar 44100 -y "{mp3_file}"')
    os.remove(out_file)

    print(f"✔ Downloaded and converted to MP3: {yt.title}")

def process_video(url, download_type, output_path):
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        if download_type == "1":
            download_mp4(yt, output_path)
        elif download_type == "2":
            download_mp3(yt, output_path)
        else:
            print("❌ Invalid download type")
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")

def main():
    print("🎥 YouTube Downloader with MP4/MP3, Playlist & Progress Support")
    url = input("Enter YouTube video or playlist URL: ").strip()

    try:
        is_playlist = "playlist" in url.lower()
        download_type = input("Download as (1) MP4 (video) or (2) MP3 (audio)? Enter 1 or 2: ").strip()
        output_path = input("Enter output directory (default is current folder): ").strip() or "."

        if is_playlist:
            pl = Playlist(url)
            videos = pl.video_urls
            print(f"\n📃 Playlist contains {len(videos)} videos.\n")
            for i, video_url in enumerate(tqdm(videos, desc="Downloading playlist", unit="video")):
                process_video(video_url, download_type, output_path)
        else:
            process_video(url, download_type, output_path)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
