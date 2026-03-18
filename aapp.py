import streamlit as st
from supabase import create_client
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import google.generativeai as genai
import os

# Load env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Init
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
model = SentenceTransformer("all-MiniLM-L6-v2")
genai.configure(api_key=GEMINI_API_KEY)

gemini_model = genai.GenerativeModel("gemini-flash-latest")

st.set_page_config(page_title="News RAG Chatbot", layout="wide")

# -------------------------------
# Session State Init
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

    # Show chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # User input
    if prompt := st.chat_input("Ask about this story..."):

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Embed query
        query_embedding = model.encode(prompt).tolist()

        # Retrieve articles
        result = supabase.rpc(
            "match_articles_by_story",
            {
                "query_embedding": query_embedding,
                "match_count": 5,
                "input_story_id": st.session_state.selected_story_id
            }
        ).execute()

        articles = result.data

        # Build context
        context = ""
        for item in articles:
            context += f"""
Title: {item['article_title']}
Source: {item['article_source']}
URL: {item['article_url']}
Content: {item['article_content']}
---
"""

        # Gemini prompt
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

        st.session_state.messages.append({"role": "assistant", "content": answer})

        with st.chat_message("assistant"):
            st.write(answer)