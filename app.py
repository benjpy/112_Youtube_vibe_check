import streamlit as st
import utils
import analysis
import time

# Page Config
st.set_page_config(
    page_title="YouTube Vibe Check",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Modern Look
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #f0f2f6;
        color: #31333F;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1E1E1E;
        font-weight: 700;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #FF0000;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #CC0000;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Cards/Containers */
    .css-1r6slb0 {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Custom Container Class (if we use st.markdown divs) */
    .custom-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Video Info */
    .video-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .video-channel {
        color: #666;
        font-size: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📺 YouTube Vibe Check")
st.markdown("Get the vibe of any YouTube video in seconds. Powered by Gemini 2.0 Flash.")

# Input Section
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("Paste YouTube URL here", placeholder="https://www.youtube.com/watch?v=...")
with col2:
    target_language = st.selectbox(
        "Output Language",
        ["Auto", "English", "French", "Spanish", "German", "Japanese", "Portuguese", "Hindi", "Arabic"]
    )

if url:
    video_id = utils.get_video_id(url)
    
    if not video_id:
        st.error("Invalid YouTube URL. Please check and try again.")
    else:
        if st.button("Analyze Vibe ✨"):
            with st.spinner("Fetching video data..."):
                # 1. Get Metadata
                metadata = utils.get_video_metadata(url)
                if not metadata:
                    st.error("Could not fetch video metadata.")
                    st.stop()
                
                # Display Video Info immediately
                st.markdown(f"""
                <div class="custom-card">
                    <div class="video-title">{metadata['title']}</div>
                    <div class="video-channel">{metadata['channel']}</div>
                    <img src="{metadata['thumbnail']}" style="width: 100%; border-radius: 10px; max-height: 400px; object-fit: cover;">
                </div>
                """, unsafe_allow_html=True)
                
                # 2. Get Transcript
                transcript = utils.get_transcript(video_id)
                if not transcript:
                    st.warning("Could not fetch transcript. Analysis might be limited.")
                
                # 3. Get Comments
                comments = utils.get_comments(url, limit=1000)
                if not comments:
                    st.warning("Could not fetch comments. Analysis might be limited.")
            
            with st.spinner("Consulting the oracle (Gemini)..."):
                # 4. Analyze
                result = analysis.analyze_video(transcript, comments, metadata, target_language=target_language)
                analysis_text = result.get("text", "")
                usage = result.get("usage", {})
                
                # Display Results
                st.markdown("### 🔮 The Vibe Report")
                
                # Fix for stray </div>: Split the markdown calls
                st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                st.markdown(analysis_text)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Token & Cost Info
                if usage:
                    prompt_tokens = usage.get("prompt_token_count", 0)
                    output_tokens = usage.get("candidates_token_count", 0)
                    total_tokens = usage.get("total_token_count", 0)
                    
                    # Cost estimation (based on Gemini 1.5 Flash pricing as a proxy/baseline)
                    # Input: $0.075 / 1M tokens
                    # Output: $0.30 / 1M tokens
                    input_cost = (prompt_tokens / 1_000_000) * 0.075
                    output_cost = (output_tokens / 1_000_000) * 0.30
                    total_cost = input_cost + output_cost
                    
                    st.info(f"""
                    **Token Usage & Cost Estimate** (based on 1.5 Flash rates):
                    - Input Tokens: {prompt_tokens:,}
                    - Output Tokens: {output_tokens:,}
                    - Total Tokens: {total_tokens:,}
                    - **Estimated Cost:** ${total_cost:.6f}
                    """)
                
                # Expander for raw data
                with st.expander("View Raw Data"):
                    st.subheader("Description")
                    st.text(metadata['description'])
                    st.subheader("Top Comments Sample")
                    for c in comments[:5]:
                        st.text(f"- {c}")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit & Gemini")
