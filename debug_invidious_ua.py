import requests

video_id = "Pwk5MPE_6zE"
api_url = f"https://iv.ggtyler.dev/api/v1/captions/{video_id}?lang=en"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print(f"Fetching: {api_url}")
try:
    r = requests.get(api_url, headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
    print("--- Body Start ---")
    print(r.text[:200])
    
    if "WEBVTT" in r.text:
        print("\nSUCCESS: Found WEBVTT header")
    else:
        print("\nFAILURE: No WEBVTT header")
except Exception as e:
    print(f"Error: {e}")
