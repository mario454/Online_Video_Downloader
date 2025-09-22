import yt_dlp
import requests
import os
import re
import unicodedata

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_DIR = os.path.join(BASE_DIR, "bin")

# Progress data and cancel downloading
progress_data = {"progress": 0, "cancel": False}
def cancel_download():
    progress_data["cancel"] = True

def progress_hook(d):
    if progress_data["cancel"]:
        progress_data["progress"] = 0.0
        raise Exception("Download canceled by user")
    
    if d['status'] == 'downloading':
        percent_str = d.get('_percent_str', '0%')
        clean_percent = re.sub(r'\x1b\[[0-9;]*m', '', percent_str).strip()
        try:
            progress_data["progress"] = float(clean_percent.replace('%','0'))
        except ValueError:
            progress_data["progress"] = 0.0


def info_mp3(url):
    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            # Extract information only from video
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])
            size_mb = 0

            # Get title of video
            title = info.get("title")

            # Filter only audio formats
            audio_formats = [f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none"]
            if audio_formats:
                # Pick the format with the highest average bitrate (abr)
                best_audio = max(audio_formats, key=lambda f: f.get("abr") or 0)
                filesize = best_audio.get("filesize")
                size_mb = round(filesize / (1024 * 1024), 2) if filesize else 0

            # Get thumbnail and download it
            cover_path = os.path.join("static", "cover.jpg")  # inside static folder
            thumbnail_url = info.get("thumbnail")
            conver = requests.get(thumbnail_url)
            with open(cover_path, "wb") as f:
                f.write(conver.content)

    except Exception as e:
        print(f"Error extracting info: {e}")
    
    return title, size_mb
        
def download_mp3(url, title):
    downloads_path = os.path.expanduser("~/Downloads")  # Get path of downloads folder

    if "youtu" in url:
        audio_quality = "bestaudio[ext=m4a]"              # Best res for audio
        
        ydl_opts = {
            "ffmpeg_location": FFMPEG_DIR,
            "format": f"{audio_quality}", # Format of video 
            "merge_output_format": "mp3", # Extension of video
            "outtmpl": os.path.join(downloads_path, f"{title.replace('/', '_')}.%(ext)s"),   # Name of file like name of video of youtube
            "progress_hooks": [progress_hook],
        }

    else:
        ydl_opts = {
        "ffmpeg_location": FFMPEG_DIR,
        "format": "best",  # download best video+audio
        "outtmpl": os.path.join(downloads_path, f"{title.replace('/', '_')}.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "progress_hooks": [progress_hook],
    }

    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"Error during download: {e}")
    finally:
        # After download or error -> delete thumbnail
        cover_path = os.path.join("static", "cover.jpg")
        if os.path.exists(cover_path):
            os.remove(cover_path)


def info_mp4(url):
    heights_sizes = dict()
    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            # Extract information only from video
            info = ydl.extract_info(url, download=False)
            # Get title of video
            title = info.get("title")
            # Get thumbnail and doenload it
            cover_path = os.path.join("static", "cover.jpg")  # inside static folder
            thumbnail_url = info.get("thumbnail")
            conver = requests.get(thumbnail_url)
            with open(cover_path, "wb") as f:
                f.write(conver.content)

            # Get formats (resolutions and sizes) of each video
            formats = info.get("formats", [])
            for f in formats:
                height = f.get("height")      # Available Resolution: 720p, ....
                ext = f.get("ext")            # Type of video: mp4
                vcodec = f.get("vcodec")       # Video codec
                filesize = f.get("filesize")  # Size by byte
                if height and ext == "mp4" and vcodec != "none":  # If resolution available EX: 720p True, 1080 False
                    heights_sizes[height] = 0
                    if filesize:
                        size_mb = round(filesize / (1024 * 1024), 2)  # Convert size to MB
                        heights_sizes[height] = size_mb
    except Exception as e:
        print(f"Error extracting info: {e}")

    sorted_heights_sizes = dict(sorted(heights_sizes.items()))

    return title, sorted_heights_sizes

def download_mp4(url, video_qual, title):
    title = unicodedata.normalize('NFKD', title)
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    # Reduce name
    if len(title) > 100:
        title = title[:100]
    
    downloads_path = os.path.expanduser("~/Downloads")  # Get path of downloads folder
    if "youtu" in url:
        video_quality = f"bestvideo[height={video_qual}][ext=mp4]" # Chosen res for video
        audio_quality = "bestaudio[ext=m4a]"              # Best res for audio
        ydl_opts = {
            "ffmpeg_location": FFMPEG_DIR,
            "format": f"{video_quality}+{audio_quality}", # Format of video 
            "merge_output_format": "mp4",                 # Extension of video
            "outtmpl": os.path.join(downloads_path, f"{title.replace('/', '_')}.%(ext)s"),   # Name of file like name of video of youtube
            "progress_hooks": [progress_hook],
        }
    else:
        ydl_opts = {
            "ffmpeg_location": FFMPEG_DIR,
            "format": "best",  # Download best available video+audio
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(downloads_path, f"{title.replace('/', '_')}.%(ext)s"),
            "progress_hooks": [progress_hook],
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"Error during download: {e}")
    finally:
        # After download or error -> delete thumbnail
        cover_path = os.path.join("static", "cover.jpg")
        if os.path.exists(cover_path):
            os.remove(cover_path)
