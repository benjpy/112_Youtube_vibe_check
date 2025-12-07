import requests
import json

video_id = "Pwk5MPE_6zE"
# Check the endpoint that we know is used in utils.py
api_url = f"https://iv.ggtyler.dev/api/v1/videos/{video_id}"

print(f"Fetching Metadata: {api_url}")
try:
    r = requests.get(api_url, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print("--- Metadata Keys ---")
        print(data.keys())
        
        # Check for captions/subtitles in the metadata
        if 'captions' in data:
            print("\n--- Captions in Metadata ---")
            print(json.dumps(data['captions'], indent=2))
        elif 'subtitles' in data:
            print("\n--- Subtitles in Metadata ---")
            print(json.dumps(data['subtitles'], indent=2))
        else:
            print("\nNo 'captions' or 'subtitles' key found.")
    else:
        print(r.text[:500])

except Exception as e:
    print(f"Error: {e}")
