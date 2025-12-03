import youtube_transcript_api
print("Module dir:", dir(youtube_transcript_api))
try:
    print("Module get_transcript:", youtube_transcript_api.get_transcript)
except AttributeError:
    print("Module get_transcript not found")

from youtube_transcript_api import YouTubeTranscriptApi
print("Class dir:", dir(YouTubeTranscriptApi))
