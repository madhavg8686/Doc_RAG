# AWS SAA-C02 RAG Study Assistant

A simple Retrieval-Augmented Generation (RAG) application for asking questions about an AWS SAA-C02 study guide.

The application extracts text from a PDF, splits it into chunks, generates vector embeddings, stores them in a FAISS index, retrieves relevant sections for a user's question, and uses Ollama to generate a grounded answer locally.

---

## 🧠 How It Works

### 1. Document Processing — Index Building

```text
             AWS SAA-C02 PDF
                    │
                    ▼
             Extract Text
                    │
                    ▼
              Text Chunks
                    │
                    ▼
          Generate Embeddings
                    │
                    ▼
              FAISS Index
```

### 2. Question Answering — RAG Pipeline

```text
             User Question
                    │
                    ▼
             Question Embedding
                    │
                    ▼
          FAISS Similarity Search
                    │
                    ▼
           Relevant PDF Chunks
                    │
                    ▼
                 Ollama
                    │
                    ▼
             Generated Answer
```

---

## ✨ Features

- 📄 PDF document processing
- ✂️ Text chunking
- 🔢 Vector embeddings
- ⚡ FAISS similarity search
- 🔎 Semantic document retrieval
- 🦙 Local LLM inference with Ollama
- 📖 Page metadata
- 🧠 RAG-based question answering
- 🐍 Python-based implementation
- 🔐 Local answer generation without requiring a paid LLM API

---

## 🛠️ Technologies

| Technology | Purpose |
|:--|:--|
| Python | Application development |
| PyPDF2 | PDF text extraction |
| NumPy | Numerical operations |
| FAISS | Vector similarity search |
| OpenAI Embeddings | Document/question embeddings |
| Ollama | Local LLM |
| Pickle | Store document metadata |
| python-dotenv | Environment variables |

---

## 📁 Project Structure

```text
Doc_RAG/
│
├── pdfvector.py
├── questionvector.py
├── rag.py
│
├── chunks.pkl
├── vector.index
│
├── SAA-C02 study guide .pdf
│
├── .env
├── .gitignore
├── pyproject.toml
└── uv.lock
```

---

## 🚀 Installation

### 1. Clone the Repository

Clone the repository to your local machine.

### 2. Create a Virtual Environment

**Windows**

```bash
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

**Linux/macOS**

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
python -m pip install faiss-cpu numpy PyPDF2 openai python-dotenv ollama
```

---

## 🦙 Install Ollama

Install Ollama on your computer.

After installation, verify it:

```bash
ollama --version
```

Pull a local language model:

```bash
ollama pull llama3.2
```

Verify the model:

```bash
ollama list
```

You should see something similar to:

```text
NAME
llama3.2
```

You can also run it directly:

```bash
ollama run llama3.2
```

> **Note:** Ollama needs to be running when the RAG application generates answers.

---

## 🔑 OpenAI API Key

The project can use OpenAI for embeddings while using Ollama for the actual answer generation.

Create a `.env` file:

```dotenv
OPENAI_API_KEY=your_api_key_here
```

The application reads the key from the environment.

---

## 🔐 Security

- Never commit `.env` to GitHub.

Recommended `.gitignore`:

```gitignore
# Python
.venv/
__pycache__/
*.pyc

# Environment variables
.env
.env.*

# Generated vector database
*.index
*.pkl

# Documents
*.pdf

# IDE
.idea/
.vscode/
```

> ⚠️ **Important:** If an API key is accidentally exposed, revoke it immediately and create a new one.

---

## 📄 Create the Vector Database

Place your study guide PDF in the project directory:

```text
SAA-C02 study guide .pdf
```

Run:

```bash
python pdfvector.py
```

The script performs:

```text
PDF
 ↓
Text Extraction
 ↓
Text Chunking
 ↓
OpenAI Embeddings
 ↓
FAISS
 ↓
vector.index
chunks.pkl
```

After successful processing, you should have:

```text
vector.index
chunks.pkl
```

---

## 🔎 Ask Questions

Start the question/RAG application:

```bash
python questionvector.py
```

**Example:**

```text
Enter your question:

What is Amazon S3?
```

The application:

1. Converts the question into an embedding.
2. Searches FAISS.
3. Retrieves the most relevant document chunks.
4. Sends the retrieved context to Ollama.
5. Generates an answer based on the study guide.

---

## 🦙 Ollama RAG Generation

Ollama is responsible for generating the final answer.

For example:

```text
User:
What is Amazon S3?

        ↓

Question Embedding

        ↓

FAISS Search

        ↓

Top 5 Relevant Chunks

        ↓

Study Guide Context

        ↓

Ollama / llama3.2

        ↓

Answer
```

This allows the language model to run locally rather than using a paid OpenAI chat model.

For example:

```bash
ollama pull llama3.2
```

Other models can also be used depending on your computer's RAM/GPU.

---

## 📚 RAG Pipeline

### Document Ingestion

```text
PDF
 │
 ▼
PyPDF2
 │
 ▼
Extracted Text
 │
 ▼
Chunks
 │
 ▼
OpenAI Embeddings
 │
 ▼
FAISS
```

### Question Answering

```text
Question
 │
 ▼
OpenAI Embedding
 │
 ▼
FAISS Search
 │
 ▼
Relevant Chunks
 │
 ▼
Ollama
 │
 ▼
Final Answer
```

---

## 🗃️ Generated Files

### `vector.index`

FAISS vector index containing the embeddings of the document chunks.

### `chunks.pkl`

Stores the document chunks and metadata.

Example:

```python
{
    "chunks": [...],
    "metadata": [...],
    "total_pages": 100
}
```

---

## 💡 Why Ollama?

Using Ollama provides several advantages:

- Local LLM execution
- No OpenAI chat-completion cost
- Data can remain on the local machine
- Easy to switch between different open models
- Useful for experimenting with RAG

For example:

```bash
ollama pull llama3.2
```

Other models can also be used depending on your computer's RAM/GPU.

---

## 🔮 Future Improvements

Possible improvements include:

- Multiple PDF support
- Upload documents dynamically
- Document metadata filtering
- Improved chunking
- Reranking
- Conversation history
- Better source citations
- Local embedding models
- Persistent vector databases
- Configurable Ollama models
- RAG evaluation
- Deployment to a server

---

## 🎯 Purpose

The current implementation uses FAISS for retrieval and Ollama for local answer generation.

---

## 📜 License

This project is intended for educational purposes.

Make sure you have the appropriate rights to use and distribute any documents processed by the application.
