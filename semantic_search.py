from supabase import create_client
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

model = SentenceTransformer("all-MiniLM-L6-v2")

question = input("Ask a news question: ")

query_embedding = model.encode(question).tolist()

result = supabase.rpc(
    "match_news",
    {
        "query_embedding": query_embedding,
        "match_count": 5
    }
).execute()

print("\nMost relevant news:\n")

for item in result.data:
    print("Title:", item["content_title"])
    print("Summary:", item["content_summary"])
    print("Similarity:", item["similarity"])
    print("------")