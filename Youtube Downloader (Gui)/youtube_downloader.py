#!/usr/bin/env python3

import os
import threading
import re
from tkinter import *
from tkinter import filedialog, messagebox
from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
import subprocess

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_mp4(yt, output_path):
    stream = yt.streams.get_highest_resolution()
    status_label.config(text=f"Downloading video: {yt.title}")
    stream.download(output_path=output_path)
    status_label.config(text=f"✔ Downloaded: {yt.title}")

def download_mp3(yt, output_path):
    audio_stream = yt.streams.filter(only_audio=True).first()
    status_label.config(text=f"Downloading audio: {yt.title}")
    out_file = audio_stream.download(output_path=output_path)

    base, _ = os.path.splitext(out_file)
    mp3_file = base + ".mp3"

    try:
        subprocess.run([
            'ffmpeg', '-loglevel', 'quiet', '-i', out_file,
            '-vn', '-ab', '192k', '-ar', '44100', '-y', mp3_file
        ], check=True)
        os.remove(out_file)
        status_label.config(text=f"✔ Downloaded and converted: {yt.title}")
    except subprocess.CalledProcessError:
        status_label.config(text=f"❌ Conversion failed: {yt.title}")

def process_video(url, download_type, output_path):
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        yt.title = sanitize_filename(yt.title)
        if download_type == "mp4":
            download_mp4(yt, output_path)
        else:
            download_mp3(yt, output_path)
    except Exception as e:
        status_label.config(text=f"❌ Failed: {url}\n{e}")

def start_download():
    url = url_entry.get().strip()
    download_type = format_var.get()
    output_path = folder_entry.get().strip() or "."

    YOUTUBE_URL_PATTERN = re.compile(
        r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$'
    )

    if not url:
        messagebox.showwarning("Input Error", "Please enter a YouTube URL.")
        return

    if not YOUTUBE_URL_PATTERN.match(url):
        messagebox.showerror("Invalid URL", "The URL entered is not a valid YouTube link.")
        return

    def download_thread():
        try:
            if "list=" in url:
                pl = Playlist(url)
                videos = pl.video_urls
                for video_url in videos:
                    process_video(video_url, download_type, output_path)
            else:
                process_video(url, download_type, output_path)
            messagebox.showinfo("Done", "Download(s) completed!")
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{e}")
        finally:
            status_label.config(text="Ready")

    threading.Thread(target=download_thread).start()

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_entry.delete(0, END)
        folder_entry.insert(0, folder)

# GUI Setup
root = Tk()
root.title("YouTube Downloader by NOTNA (MP4/MP3)")
root.geometry("500x250")
root.resizable(False, False)

Label(root, text="YouTube URL:").pack(pady=5)
url_entry = Entry(root, width=60)
url_entry.pack(pady=5)

format_var = StringVar(value="mp4")
format_frame = Frame(root)
Radiobutton(format_frame, text="MP4 (video)", variable=format_var, value="mp4").pack(side=LEFT, padx=10)
Radiobutton(format_frame, text="MP3 (audio)", variable=format_var, value="mp3").pack(side=LEFT, padx=10)
format_frame.pack(pady=5)

Label(root, text="Output Folder:").pack(pady=5)
folder_frame = Frame(root)
folder_entry = Entry(folder_frame, width=45)
folder_entry.pack(side=LEFT)
Button(folder_frame, text="Browse", command=browse_folder).pack(side=LEFT, padx=5)
folder_frame.pack(pady=5)

Button(root, text="Download", command=start_download, width=20, bg="green", fg="white").pack(pady=10)

status_label = Label(root, text="Ready", fg="blue")
status_label.pack(pady=5)

root.mainloop()
