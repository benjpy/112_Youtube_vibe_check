from youtube_transcript_api import YouTubeTranscriptApi
import inspect

print("--- Attributes of YouTubeTranscriptApi class ---")
print(dir(YouTubeTranscriptApi))

try:
    api = YouTubeTranscriptApi()
    print("\n--- Attributes of YouTubeTranscriptApi instance ---")
    print(dir(api))
except Exception as e:
    print(f"\nCould not instantiate: {e}")
