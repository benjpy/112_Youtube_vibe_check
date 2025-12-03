from youtube_transcript_api import YouTubeTranscriptApi

video_id = "dQw4w9WgXcQ" # Rick Roll

print("Testing list:")
try:
    print(YouTubeTranscriptApi.list(video_id))
except Exception as e:
    print(f"list failed: {e}")

print("Testing fetch:")
try:
    print(YouTubeTranscriptApi.fetch(video_id))
except Exception as e:
    print(f"fetch failed: {e}")
