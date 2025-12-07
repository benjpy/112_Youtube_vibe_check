import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Check Streamlit secrets as fallback (for Cloud deployment)
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in .env (local) or Streamlit Secrets (cloud).")
    return genai.Client(api_key=api_key)

def analyze_video(transcript, comments, video_metadata, target_language="Auto"):
    """
    Analyzes the video transcript and comments using Gemini.
    """
    client = get_gemini_client()
    
    # Prepare the prompt
    title = video_metadata.get('title', 'Unknown Title')
    channel = video_metadata.get('channel', 'Unknown Channel')
    description = video_metadata.get('description', '')
    
    # Truncate inputs if they are too long to avoid token limits (basic safety)
    truncated_transcript = transcript[:50000] if transcript else "No transcript available."
    comments_text = "\n".join([f"- {c}" for c in comments])
    
    language_instruction = ""
    if target_language != "Auto":
        language_instruction = f"Please provide the output in {target_language}."
    else:
        language_instruction = "Please provide the output in the same language as the video and comments."

    prompt = f"""
    You are an expert social media analyst. I will provide you with data about a YouTube video.
    
    **Video Title:** {title}
    **Channel:** {channel}
    **Description:** {description[:1000]}...
    
    **Transcript (excerpt):**
    {truncated_transcript}
    
    **Top Comments (with like counts):**
    {comments_text}
    
    Please provide an analysis in the following structured format (Markdown).
    {language_instruction}
    
    ## 🗣️ Speaker Analysis
    Identify the main speakers based on the transcript and context. For each speaker, summarize what the comments say about them. 
    **Important:** Pay close attention to the like counts on comments. Comments with high like counts represent the majority opinion and should be given significantly more weight in your summary. If there are no specific comments about a speaker, infer the general sentiment towards them from the video content and overall reaction.
    
    ## ✨ Vibe Check (General Summary)
    What is the overall sentiment of the video? What are people saying? Is it positive, negative, controversial, funny, educational? Summarize the general "vibe" of the audience reaction, again giving more weight to highly liked comments.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        
        usage = {}
        if response.usage_metadata:
            usage = {
                "prompt_token_count": response.usage_metadata.prompt_token_count,
                "candidates_token_count": response.usage_metadata.candidates_token_count,
                "total_token_count": response.usage_metadata.total_token_count
            }
            
        return {
            "text": response.text,
            "usage": usage
        }
    except Exception as e:
        return {
            "text": f"Error generating analysis: {e}",
            "usage": {}
        }
