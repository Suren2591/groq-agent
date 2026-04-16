import streamlit as st
from blog_agent import youtube_to_blog

st.set_page_config(page_title="Blog Generator", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        max-width: 800px;
        margin: auto;
    }
    .title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .content {
        font-size: 18px;
        line-height: 1.8;
        color: #333;
    }
    .credit {
        font-size: 12px;
        color: gray;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎥 YouTube → Blog Generator")

youtube_url = st.text_input("Paste YouTube URL")

if st.button("Generate Blog"):
    if youtube_url:
        with st.spinner("Generating blog..."):
            data = youtube_to_blog(youtube_url)

        st.success("Blog generated!")

        # 🖼️ Image
        if data["image_url"]:
            st.image(data["image_url"], use_container_width=True)

        # 📰 Title
        st.title(data["title"])

        # ✍️ CONTENT (THIS IS THE IMPORTANT LINE)
        st.markdown(data["content"])