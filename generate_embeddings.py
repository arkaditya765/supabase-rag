from supabase import create_client
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Fetching rows from Supabase...")

response = supabase.table("newspresso_aggregated_news_in") \
    .select("id,content_title,content_description,content_summary,content,embedding") \
    .execute()

rows = response.data

print("Rows fetched:", len(rows))

for row in tqdm(rows):

    if row["embedding"] is not None:
        continue

    text = " ".join([
        str(row.get("content_title", "")),
        str(row.get("content_description", "")),
        str(row.get("content_summary", "")),
        str(row.get("content", ""))
    ])

    embedding = model.encode(text).tolist()

    supabase.table("newspresso_aggregated_news_in") \
        .update({"embedding": embedding}) \
        .eq("id", row["id"]) \
        .execute()

print("Embeddings generated successfully")