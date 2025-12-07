import re
import os
import requests
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

# List of public Invidious instances to try
# Prioritize instances known to have working APIs and good uptime
INVIDIOUS_INSTANCES = [
    "https://inv.tux.pizza",
    "https://invidious.jing.rocks", 
    "https://vid.puffyan.us",
    "https://invidious.nerdvpn.de",
    "https://iv.ggtyler.dev" # Moved to bottom as it was returning HTML for captions
]

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
        "socket_timeout": 5, # Fail fast if blocked
        "retries": 1,
    }

    yt_error = None
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
            yt_error = str(e)
            print(f"yt-dlp metadata error: {e}")
            print("Falling back to Invidious…")

            # ---- FALLBACK USING INVIDIOUS (Multi-Instance) ----  
            video_id = get_video_id(url)
            if not video_id:
                return None

            last_inv_error = None
            for instance in INVIDIOUS_INSTANCES:
                try:
                    import requests
                    api_url = f"{instance}/api/v1/videos/{video_id}"
                    # Short timeout to fail fast and try next
                    r = requests.get(api_url, timeout=5)
                    if r.status_code != 200:
                         raise Exception(f"Status {r.status_code}")
                    
                    # Verify it's JSON
                    try:
                        data = r.json()
                    except:
                        raise Exception("Response was not JSON")

                    return {
                        'title': data.get('title'),
                        'description': data.get('description'),
                        'channel': data.get('author'),
                        'thumbnail': data.get('videoThumbnails', [{}])[0].get('url'),
                        'duration': data.get('lengthSeconds')
                    }
                except Exception as e:
                    last_inv_error = e
                    continue # Try next instance
            
            # If loop finishes without return
            raise Exception(f"Video metadata fetch failed. yt-dlp Error: {yt_error}. Invidious Fallback Error: {last_inv_error}")

def _parse_webvtt(vtt_content):
    """
    Parses WebVTT content to extract just the text.
    Removes timestamps, tags, and header.
    """
    lines = vtt_content.splitlines()
    text_lines = []
    
    # Simple state machine or regex could work. 
    # WebVTT typically has:
    # WEBVTT
    #
    # 00:00:00.000 --> 00:00:05.000
    # Text line
    
    timestamp_pattern = re.compile(r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line == "WEBVTT":
            continue
        if timestamp_pattern.match(line):
            continue
        # Skip pure numbers (sequence identifiers, though not always present in WebVTT)
        if line.isdigit():
            continue
            
        # Remove HTML-like tags (e.g. <c.colorE5E5E5>)
        line = re.sub(r'<[^>]+>', '', line)
        
        # Deduplicate logical lines if needed, but for now just gather
        # Avoid empty lines after cleaning
        if line:
            text_lines.append(line)
            
    return " ".join(text_lines)

def get_transcript(video_id):
    """
    Fetches the transcript of the video.
    Priority:
    1. youtube-transcript-api (standard)
    2. youtube-transcript-api (with cookies.txt if available)
    3. Invidious API (captions fallback)
    """
    
    # --- Attempt 1 & 2: youtube-transcript-api (Standard + Cookies) ---
    exceptions = []
    
    # Check for cookies file
    cookies_file = "cookies.txt"
    has_cookies = os.path.exists(cookies_file)
    
    # Options to try: [No Cookies] then [Cookies] (if file exists)
    # Actually, if cookies exist, we might want to try them first or second? 
    # Usually standard first is better for privacy/simplicity, cookies as backup.
    
    attempts = [("Standard", None)]
    if has_cookies:
        attempts.append(("Cookies", cookies_file))
        
    for name, cookie_path in attempts:
        try:
            # Note: We need to re-instantiate for each attempt to clear state if any
            api = YouTubeTranscriptApi()
            
            # list(video_id) fetches available transcripts
            # Try newer API (list_transcripts) first, then fallback to legacy (list)
            # list(video_id) fetches available transcripts
            # Try newer API (list_transcripts) first
            # If cookie_path is provided, we use it.
            
            if cookie_path:
                 transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, cookies=cookie_path)
            else:
                 transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # NEWER API USAGE
            transcript = None
            try:
                transcript = transcript_list.find_transcript(['en'])
            except:
                try:
                     transcript = transcript_list.find_generated_transcript(['en'])
                except:
                     for t in transcript_list:
                         transcript = t
                         break
            
            if not transcript:
                raise Exception("No transcript found in list.")
            
            fetched_transcript = transcript.fetch()
            full_text = " ".join([item['text'] for item in fetched_transcript])
            return full_text

        except Exception as e:
            exceptions.append(f"Method '{name}' failed: {e}")
            
    # --- Attempt 3: Invidious API Fallback (Multi-Instance) ---
    print("Falling back to Invidious for transcript...")
    last_inv_error = None
    
    for instance in INVIDIOUS_INSTANCES:
        try:
            api_url = f"{instance}/api/v1/captions/{video_id}?lang=en"
            
            # Add User-Agent to avoid blocking
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            r = requests.get(api_url, headers=headers, timeout=5)
            if r.status_code != 200:
                raise Exception(f"Status {r.status_code}")
                
            vtt_content = r.text
            # If response is HTML (often error page), fail
            if "<html" in vtt_content.lower() or "<!doctype" in vtt_content.lower():
                raise Exception("Response looks like HTML, not VTT")
                
            full_text = _parse_webvtt(vtt_content)
            
            if not full_text.strip():
                 raise Exception("Parsed empty text from Invidious VTT")
                 
            return full_text
            
        except Exception as e:
            last_inv_error = e
            continue

    exceptions.append(f"Method 'Invidious' failed (all instances): {last_inv_error}")

    # If all failed
    final_error = "\n".join(exceptions)
    raise Exception(f"All transcript fetch methods failed.\n{final_error}")

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
        "socket_timeout": 5, # Fail fast if blocked
        "retries": 1,
    }
    
    yt_error = None
    comments = None

    # ---- First try yt-dlp ----
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            comments = info.get("comments", [])
        except Exception as e:
            yt_error = str(e)
            comments = None

    # ---- Fallback to Invidious (Multi-Instance) ----
    if comments is None:
        last_inv_error = None
        for instance in INVIDIOUS_INSTANCES:
            try:
                import requests
                video_id = get_video_id(url)
                api_url = f"{instance}/api/v1/comments/{video_id}"
                r = requests.get(api_url, timeout=5) # fast timeout
                if r.status_code != 200:
                    raise Exception(f"Status {r.status_code}")
                
                try:
                    data = r.json()
                except:
                    raise Exception("Response was not JSON")
    
                comments = [
                    {"text": c.get("content"), "like_count": c.get("likes")}
                    for c in data.get("comments", [])
                ]
                break # Success
            except Exception as e2:
                last_inv_error = e2
                continue
        
        if comments is None:
             raise Exception(f"Comments fetch failed. yt-dlp Error: {yt_error}. Invidious Fallback Error: {last_inv_error}")

    # ---- Sort → format → return ----
    if comments:
        comments.sort(key=lambda x: x.get("like_count", 0) or 0, reverse=True)

    formatted = []
    for c in comments[:limit]:
        text = c.get("text")
        likes = c.get("like_count", 0) or 0
        if text:
            formatted.append(f"(Likes: {likes}) {text}")

    return formatted