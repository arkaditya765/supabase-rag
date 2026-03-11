from supabase import create_client
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google import genai
import os

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize Gemini client
gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Ask user question
question = input("Ask a news question: ")

print("\nProcessing...\n")

# Convert question to embedding
query_embedding = embedding_model.encode(question).tolist()

# Retrieve relevant news from Supabase
result = supabase.rpc(
    "match_news",
    {
        "query_embedding": query_embedding,
        "match_count": 5
    }
).execute()

# Build context from retrieved articles
context = ""

for item in result.data:
    context += f"Title: {item['content_title']}\n"
    context += f"Summary: {item['content_summary']}\n\n"

# Create prompt for Gemini
prompt = f"""
You are a news assistant.

Use the news articles below to answer the user's question.

News Articles:
{context}

User Question:
{question}

Give a clear and concise answer based only on the news provided.
"""

# Generate answer using Gemini
response = gemini.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt
)

# Print final answer
print("Answer:\n")
print(response.text)