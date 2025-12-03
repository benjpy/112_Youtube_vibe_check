from youtube_transcript_api import YouTubeTranscriptApi

try:
    api = YouTubeTranscriptApi()
    transcript_list = api.list("dQw4w9WgXcQ")
    
    print("Finding transcript...")
    # Try to find English or auto-generated English
    try:
        transcript = transcript_list.find_transcript(['en'])
        print("Found manual English")
    except:
        try:
            transcript = transcript_list.find_generated_transcript(['en'])
            print("Found auto-generated English")
        except:
            # Fallback to whatever is there
            transcript = transcript_list[0] # Not subscriptable? iterate?
            print("Fallback to first available")

    print("Fetching...")
    result = transcript.fetch()
    print(f"Fetched {len(result)} lines")
    print(result[0])

except Exception as e:
    print(f"Failed: {e}")
