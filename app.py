import streamlit as st
from supabase import create_client
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import google.generativeai as genai
import urllib.parse
import os

# -------------------------------
# Load env
# -------------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# -------------------------------
# Init clients
# -------------------------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
model = SentenceTransformer("all-MiniLM-L6-v2")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-flash-latest")

st.set_page_config(page_title="News RAG Chatbot", layout="wide")

# -------------------------------
# Helper: favicon
# -------------------------------
def get_favicon(url):
    domain = urllib.parse.urlparse(url).netloc
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=32"

# -------------------------------
# Session State
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "select"

if "selected_story_id" not in st.session_state:
    st.session_state.selected_story_id = None

if "selected_story_title" not in st.session_state:
    st.session_state.selected_story_title = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# SCREEN 1 — STORY SELECTION
# -------------------------------
if st.session_state.page == "select":

    st.title("📰 Select a News Story")

    stories = supabase.table("newspresso_aggregated_news_in_duplicate") \
        .select("id, content_title") \
        .limit(50) \
        .execute()

    story_list = stories.data

    for story in story_list:
        if st.button(story["content_title"]):
            st.session_state.selected_story_id = story["id"]
            st.session_state.selected_story_title = story["content_title"]
            st.session_state.page = "chat"
            st.session_state.messages = []
            st.rerun()

# -------------------------------
# SCREEN 2 — CHATBOT
# -------------------------------
elif st.session_state.page == "chat":

    st.title(f"🧠 Chat: {st.session_state.selected_story_title}")

    # Back button
    if st.button("⬅ Back to stories"):
        st.session_state.page = "select"
        st.session_state.messages = []
        st.rerun()

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)

    # User input
    if prompt := st.chat_input("Ask about this story..."):

        # Show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Step 1: Embed query
        query_embedding = model.encode(prompt).tolist()

        # Step 2: Retrieve articles (story-specific)
        result = supabase.rpc(
            "match_articles_by_story",
            {
                "query_embedding": query_embedding,
                "match_count": 5,
                "input_story_id": st.session_state.selected_story_id
            }
        ).execute()

        articles = result.data

        # Step 3: Build context
        context = ""
        for item in articles:
            context += f"""
Title: {item['article_title']}
Source: {item['article_source']}
URL: {item['article_url']}
Content: {item['article_content']}
---
"""

        # Step 4: Ask Gemini
        full_prompt = f"""
You are a news assistant.

Answer ONLY using the provided articles.
Give a clear answer and cite sources.

Articles:
{context}

Question:
{prompt}
"""

        response = gemini_model.generate_content(full_prompt)
        answer = response.text

        # Step 5: Format response with sources
        formatted_answer = answer + "\n\n### Sources:\n"

        for item in articles:
            favicon = get_favicon(item["article_url"])
            formatted_answer += f"""
<div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
    <img src="{favicon}" width="20">
    <a href="{item['article_url']}" target="_blank">{item['article_title']}</a>
</div>
"""

        # Save to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": formatted_answer
        })

        # Display response
        with st.chat_message("assistant"):
            st.markdown(formatted_answer, unsafe_allow_html=True)