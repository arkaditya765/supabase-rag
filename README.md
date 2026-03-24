# 📰 NewsPress RAG Chatbot

An intelligent **story-specific news chatbot** built using **RAG (Retrieval-Augmented Generation)**.
It answers user queries by retrieving relevant articles from a database and generating grounded responses with citations.

---

## 🚀 Features

* 🧠 **RAG-based QA** – Answers using only stored news articles
* 📰 **Story-specific chat** – Ask questions per news story
* 🔗 **Numbered citations** – Inline references like `[1], [2]`
* 🌐 **Multilingual support**:

  * English → English response
  * Hindi → Hindi (Devanagari) response
  * Hinglish → Hinglish (Latin script) response
* 🎯 **Accurate retrieval** using embeddings (Sentence Transformers)
* ⚡ **Fast UI** built with Streamlit
* 🌍 **Supabase backend** for scalable storage

---

## 🏗️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Supabase (PostgreSQL + RPC)
* **Embeddings:** sentence-transformers (`all-MiniLM-L6-v2`)
* **LLM:** Google Gemini (Generative AI)
* **Language Handling:** Prompt-based multilingual detection

---

## 📂 Project Structure

```
├── app.py                # Main Streamlit app
├── requirements.txt     # Dependencies
├── README.md            # Project documentation
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/newspress-rag-chatbot.git
cd newspress-rag-chatbot
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Add Environment Variables

#### 👉 For Local Development (`.env`)

```
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
GEMINI_API_KEY=your_key
```

#### 👉 For Streamlit Cloud

Go to:

```
App Settings → Secrets
```

Add:

```toml
SUPABASE_URL = "your_url"
SUPABASE_KEY = "your_key"
GEMINI_API_KEY = "your_key"
```

---

### 5️⃣ Run the App

```bash
streamlit run app.py
```

---

## 🧠 How It Works

1. User selects a news story
2. User asks a question
3. Query is converted into embeddings
4. Supabase RPC retrieves **most relevant articles**
5. Context is sent to Gemini
6. Model generates:

   * Grounded answer
   * Inline citations `[1], [2]`
7. Sources are displayed below with clickable links

---

## 🔍 Example

### Input:

```
kya ho raha hai is story me?
```

### Output:

```
Is story me Federal Reserve interest rates ko stable rakhne ki planning kar raha hai [1][2].

### Sources:
[1] Article link  
[2] Article link  
```

---

## 📌 Key Design Decisions

* ❌ No hallucination → answers strictly from articles
* ✅ Article-level retrieval instead of story-level
* ✅ Clean citation format `[1], [2]`
* ✅ Language auto-detection for better UX

---

## 🚀 Future Improvements

* ⭐ Highlight most relevant source
* 📊 Confidence scores
* 🔎 Search + filtering
* ⚡ Caching for faster responses
* 🌐 Deployment with custom domain

---

## 🤝 Contributing

Feel free to fork and improve this project.

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 👨‍💻 Author

**Arkaditya**
B.Tech Cloud Computing | AI Enthusiast
