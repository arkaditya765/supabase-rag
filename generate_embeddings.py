from supabase import create_client
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

# Load env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Fetch articles WITHOUT embeddings
response = supabase.table("news_articles") \
    .select("id, article_content") \
    .is_("embedding", None) \
    .limit(1000) \
    .execute()

articles = response.data

print(f"Found {len(articles)} articles to process...")

for article in articles:
    text = article["article_content"]

    if not text:
        continue

    # Generate embedding
    embedding = model.encode(text).tolist()

    # Update in DB
    supabase.table("news_articles") \
        .update({"embedding": embedding}) \
        .eq("id", article["id"]) \
        .execute()

    print(f"Updated article {article['id']}")

print("✅ Embeddings complete")