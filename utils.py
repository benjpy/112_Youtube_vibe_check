import re
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    # Examples:
    # https://www.youtube.com/watch?v=VIDEO_ID
    # https://youtu.be/VIDEO_ID
    # https://www.youtube.com/embed/VIDEO_ID
    
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

def get_video_metadata(url):
    """
    Fetches video metadata (title, description, channel) using yt-dlp.
    Includes User-Agent to avoid 403 on Streamlit Cloud.
    Has fallback to Invidious if yt-dlp is blocked.
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title'),
                'description': info.get('description'),
                'channel': info.get('uploader'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration')
            }
        except Exception as e:
            print(f"yt-dlp metadata error: {e}")
            print("Falling back to Invidious…")

            # ---- FALLBACK USING INVIDIOUS ----  
            video_id = get_video_id(url)
            if not video_id:
                return None

            try:
                import requests
                api_url = f"https://iv.ggtyler.dev/api/v1/videos/{video_id}"
                r = requests.get(api_url, timeout=8)
                data = r.json()

                return {
                    'title': data.get('title'),
                    'description': data.get('description'),
                    'channel': data.get('author'),
                    'thumbnail': data.get('videoThumbnails', [{}])[0].get('url'),
                    'duration': data.get('lengthSeconds')
                }
            except Exception as e2:
                print("Invidious fallback failed:", e2)
                return None

def get_transcript(video_id):
    """
    Fetches the transcript of the video using youtube-transcript-api.
    """
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        
        transcript = None
        # Try to find manual English transcript
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            # Try to find auto-generated English transcript
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
            except:
                # Fallback: take the first available transcript (any language)
                try:
                    for t in transcript_list:
                        transcript = t
                        break
                except:
                    pass
        
        if not transcript:
            print("No transcript found.")
            return None

        fetched_transcript = transcript.fetch()
        # Combine text into a single string. 
        # Note: fetched_transcript is a list of objects with .text attribute
        full_text = " ".join([item.text for item in fetched_transcript])
        return full_text
            
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def get_comments(url, limit=1000):
    """
    Scrapes the top comments.
    Falls back to Invidious if yt-dlp is blocked (403).
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "getcomments": True,
        "playlist_items": "0",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    # ---- First try yt-dlp ----
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            comments = info.get("comments", [])
        except Exception as e:
            print("yt-dlp comments error:", e)
            comments = None

    # ---- Fallback to Invidious ----
    if comments is None:
        try:
            import requests
            video_id = get_video_id(url)
            api_url = f"https://iv.ggtyler.dev/api/v1/comments/{video_id}"
            r = requests.get(api_url, timeout=10)
            data = r.json()

            comments = [
                {"text": c.get("content"), "like_count": c.get("likes")}
                for c in data.get("comments", [])
            ]
        except Exception as e2:
            print("Invidious comments fallback failed:", e2)
            return []

    # ---- Sort → format → return ----
    comments.sort(key=lambda x: x.get("like_count", 0) or 0, reverse=True)

    formatted = []
    for c in comments[:limit]:
        text = c.get("text")
        likes = c.get("like_count", 0) or 0
        if text:
            formatted.append(f"(Likes: {likes}) {text}")

    return formatted