import streamlit as st
from supabase import create_client
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google import genai
import os

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize clients
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.title("📰 Newspresso AI Chatbot")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask about the news..."):

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    # Generate embedding
    query_embedding = embedding_model.encode(prompt).tolist()

    # Retrieve news from Supabase
    result = supabase.rpc(
        "match_news",
        {
            "query_embedding": query_embedding,
            "match_count": 5
        }
    ).execute()

    # Build context
    context = ""

    for item in result.data:
        context += f"Title: {item['content_title']}\n"
        context += f"Summary: {item['content_summary']}\n\n"

    # Create prompt
    rag_prompt = f"""
    You are a helpful news assistant.

    Use the news articles below to answer the question.

    News Articles:
    {context}

    Question:
    {prompt}

    Provide a clear answer based on the articles.
    """

    # Generate answer with Gemini
    response = gemini.models.generate_content(
        model="gemini-flash-latest",
        contents=rag_prompt
    )

    answer = response.text

    # Show assistant message
    with st.chat_message("assistant"):
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})