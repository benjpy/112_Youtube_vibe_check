import utils
import sys

def test_fetch(video_id):
    print(f"Testing transcript fetch for video ID: {video_id}")
    try:
        transcript = utils.get_transcript(video_id)
        if transcript:
            print(f"SUCCESS: Fetched transcript. Length: {len(transcript)} chars.")
            print(f"Preview: {transcript[:100]}...")
        else:
            print("FAILURE: Transcript is empty/None")
    except Exception as e:
        print(f"FAILURE: Exception occurred: {e}")

if __name__ == "__main__":
    # Video from the user's report
    video_id = "Pwk5MPE_6zE" 
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
        
    test_fetch(video_id)
