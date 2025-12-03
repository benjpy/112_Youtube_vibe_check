from youtube_transcript_api import YouTubeTranscriptApi
import pkg_resources

try:
    version = pkg_resources.get_distribution("youtube-transcript-api").version
    print(f"Version: {version}")
except:
    print("Version not found")

try:
    api = YouTubeTranscriptApi()
    print("Instantiated successfully")
    try:
        print("Calling list on instance:")
        print(api.list("dQw4w9WgXcQ"))
    except Exception as e:
        print(f"Instance list failed: {e}")
        
    try:
        print("Calling get_transcript on instance:")
        print(api.get_transcript("dQw4w9WgXcQ"))
    except Exception as e:
        print(f"Instance get_transcript failed: {e}")

except Exception as e:
    print(f"Instantiation failed: {e}")
