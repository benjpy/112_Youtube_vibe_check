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
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
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
            print(f"Error fetching metadata: {e}")
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
    Scrapes the top comments using yt-dlp.
    Returns a list of strings formatted as "(Likes: X) Comment text".
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'getcomments': True,
        'playlist_items': '0', # Only the video itself
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            comments = info.get('comments', [])
            
            # Sort by like_count if available to get "top" comments
            if comments:
                comments.sort(key=lambda x: x.get('like_count', 0) or 0, reverse=True)
            
            # Return top N comments with like count
            formatted_comments = []
            for c in comments[:limit]:
                text = c.get('text')
                likes = c.get('like_count', 0) or 0
                if text:
                    formatted_comments.append(f"(Likes: {likes}) {text}")
            
            return formatted_comments
        except Exception as e:
            print(f"Error fetching comments: {e}")
            return []
