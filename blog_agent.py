import os
from dotenv import load_dotenv
from config import Config

Config.validate()  # 👈 validate environment variables
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import re

client = Groq(api_key=Config.GROQ_API_KEY)
UNSPLASH_ACCESS_KEY = Config.UNSPLASH_ACCESS_KEY  # Free at unsplash.com/developers

# ─────────────────────────────────────────
# HELPER — Extract YouTube Video ID
# ─────────────────────────────────────────
def extract_video_id(url):
    pattern = r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise ValueError("Invalid YouTube URL")

# ─────────────────────────────────────────
# HELPER — Fetch YouTube Transcript
# ─────────────────────────────────────────
def fetch_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try English first
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            transcript = transcript_list.find_transcript(
                [t.language_code for t in transcript_list]
            )

        data = transcript.fetch()
        return " ".join([t["text"] for t in data])

    except Exception as e:
        return f"❌ Transcript error: {str(e)}"

# ─────────────────────────────────────────
# AGENT 1 — Description Writer
# ─────────────────────────────────────────
def agent_description(transcript):
    print("\n📝 Agent 1: Writing description...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a professional blog writer.

Convert the given YouTube transcript into a well-structured blog post in MARKDOWN format.

Requirements:
- Use headings (##, ###)
- Use short paragraphs
- Add bullet points where useful
- Include an engaging introduction
- Include a clear conclusion
- Keep it between 400–600 words
- Make it easy to read and informative
- Do NOT include the title
"""
            },
            {
                "role": "user",
                "content": f"Create a blog post from this transcript:\n\n{transcript[:4000]}"
            }
        ],
        temperature=0.7,
        max_tokens=1024
    )

    return response.choices[0].message.content

# ─────────────────────────────────────────
# AGENT 2 — Title Generator
# ─────────────────────────────────────────
def agent_title(description):
    print("🏷️  Agent 2: Generating title...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are an expert copywriter. 
                Generate 3 catchy, SEO-friendly blog titles.
                Return ONLY the titles, numbered 1-3. Nothing else."""
            },
            {
                "role": "user",
                "content": f"Generate titles for this blog:\n\n{description[:1000]}"
            }
        ],
        temperature=0.8,
        max_tokens=200
    )

    titles = response.choices[0].message.content
    # Pick the first title
    first_title = titles.split("\n")[0]
    first_title = re.sub(r"^1[\.\)]\s*", "", first_title).strip()
    return first_title, titles

# ─────────────────────────────────────────
# AGENT 3 — Image Fetcher
# ─────────────────────────────────────────
def agent_image(title):
    print("🖼️  Agent 3: Fetching image...")

    # Generate search keyword using Groq
    keyword_response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Extract 2-3 keywords from the title for an image search. Return ONLY the keywords, nothing else."
            },
            {
                "role": "user",
                "content": f"Title: {title}"
            }
        ],
        max_tokens=50
    )

    keywords = keyword_response.choices[0].message.content.strip()
    print(f"   🔍 Searching images for: {keywords}")

    # Fetch image from Unsplash
    url = f"https://api.unsplash.com/search/photos"
    params = {
        "query": keywords,
        "per_page": 1,
        "client_id": UNSPLASH_ACCESS_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data["results"]:
        image_url = data["results"][0]["urls"]["regular"]
        image_credit = data["results"][0]["user"]["name"]
        return image_url, image_credit
    else:
        return None, None

# ─────────────────────────────────────────
# AGENT 4 — Blog Merger
# ─────────────────────────────────────────
def agent_merge(title, description, image_url, image_credit):
    print("🔗 Agent 4: Merging into final blog...\n")

    blog = f"""
=====================================
📰 BLOG POST
=====================================

📌 TITLE:
{title}

🖼️  FEATURED IMAGE:
{image_url if image_url else "No image found"}
(Photo by {image_credit if image_credit else "N/A"})

📝 CONTENT:
{description}

=====================================
✅ Blog generated by Multi-Agent System
=====================================
"""
    return blog

# ─────────────────────────────────────────
# MAIN — Run All Agents
# ─────────────────────────────────────────
def youtube_to_blog(youtube_url):
    print(f"\n🚀 Starting Blog Generation for:\n{youtube_url}\n")

    # Extract video ID and transcript
    video_id = extract_video_id(youtube_url)
    print(f"✅ Video ID: {video_id}")

    transcript = fetch_transcript(video_id)
    print(f"✅ Transcript fetched ({len(transcript)} characters)")

    # Run agents
    description = agent_description(transcript)
    title, all_titles = agent_title(description)
    image_url, image_credit = agent_image(title)
    blog = agent_merge(title, description, image_url, image_credit)

    # Print all generated titles
    print("\n💡 All Generated Titles:")
    print(all_titles)

    # Print final blog
    # print(blog)
    # return blog
    return {
        "title": title,
        "content": description,
        "image_url": image_url,
        "image_credit": image_credit
    }

    # Save to file
    with open("blog_output.txt", "w") as f:
        f.write(blog)
    print("\n💾 Blog saved to blog_output.txt")

# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    youtube_url = input("\n🎥 Enter YouTube URL: ")
    youtube_to_blog(youtube_url)