from youtube_transcript_api import YouTubeTranscriptApi
print(dir(YouTubeTranscriptApi))
try:
    print(YouTubeTranscriptApi.get_transcript)
except AttributeError:
    print("get_transcript not found")
