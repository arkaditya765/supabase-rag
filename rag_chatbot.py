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

# Init clients
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
model = SentenceTransformer("all-MiniLM-L6-v2")

genai.configure(api_key=GEMINI_API_KEY)

# ⚠️ use working model (you already tested)
gemini_model = genai.GenerativeModel("gemini-pro")

# 👇 Hardcode for now (we’ll replace with UI later)
# Fetch available stories
stories = supabase.table("newspresso_aggregated_news_in_duplicate") \
    .select("id, content_title") \
    .limit(20) \
    .execute()

story_list = stories.data

print("\nAvailable Stories:\n")

for i, story in enumerate(story_list):
    print(f"{i+1}. {story['content_title']}")

# User selects story
choice = int(input("\nSelect story number: ")) - 1

selected_story_id = story_list[choice]["id"]

print(f"\n✅ Selected: {story_list[choice]['content_title']}")
while True:
    question = input("\nAsk a question (or type 'exit'): ")

    if question.lower() == "exit":
        break

    # Step 1: Embed question
    query_embedding = model.encode(question).tolist()

    # Step 2: Retrieve relevant articles (ONLY this story)
    result = supabase.rpc(
        "match_articles_by_story",
        {
            "query_embedding": query_embedding,
            "match_count": 5,
            "input_story_id": selected_story_id
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
    prompt = f"""
You are a news assistant.

Answer the question using ONLY the provided articles.
Give a clear answer and cite sources.

Articles:
{context}

Question:
{question}
"""

    response = gemini_model.generate_content(prompt)

    print("\n🧠 Answer:\n")
    print(response.text)