import os
import pickle

import faiss
import numpy as np
import ollama
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AWS SAA-C02 Study Assistant",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# SETTINGS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

INDEX_FILE = os.path.join(
    BASE_DIR,
    "vector.index"
)

CHUNKS_FILE = os.path.join(
    BASE_DIR,
    "chunks.pkl"
)

EMBEDDING_MODEL = "nomic-embed-text"

CHAT_MODEL = "llama3.2"


# ============================================================
# LOAD FAISS DATABASE
# ============================================================

@st.cache_resource
def load_database():

    if not os.path.exists(
        INDEX_FILE
    ):

        raise FileNotFoundError(
            f"vector.index not found:\n\n"
            f"{INDEX_FILE}\n\n"
            "Run pdfvector.py first."
        )

    if not os.path.exists(
        CHUNKS_FILE
    ):

        raise FileNotFoundError(
            f"chunks.pkl not found:\n\n"
            f"{CHUNKS_FILE}\n\n"
            "Run pdfvector.py first."
        )

    # Load FAISS
    index = faiss.read_index(
        INDEX_FILE
    )

    # Load chunks
    with open(
        CHUNKS_FILE,
        "rb"
    ) as f:

        data = pickle.load(f)

    chunks = data["chunks"]
    metadata = data["metadata"]

    return (
        index,
        chunks,
        metadata
    )


# ============================================================
# QUESTION EMBEDDING
# ============================================================

def create_question_embedding(
    question
):

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=question
    )

    embedding = np.array(
        [
            response["embeddings"][0]
        ],
        dtype="float32"
    )

    # Normalize for cosine similarity
    faiss.normalize_L2(
        embedding
    )

    return embedding


# ============================================================
# SEARCH FAISS
# ============================================================

def search_database(
    question,
    index,
    chunks,
    metadata,
    top_k=5
):

    question_vector = (
        create_question_embedding(
            question
        )
    )

    scores, indices = index.search(
        question_vector,
        top_k
    )

    results = []

    for score, index_id in zip(
        scores[0],
        indices[0]
    ):

        if index_id == -1:
            continue

        results.append({
            "score": float(score),
            "text": chunks[index_id],
            "metadata": metadata[index_id]
        })

    return results


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(
    question,
    results
):

    context_parts = []

    for result in results:

        page = result[
            "metadata"
        ].get(
            "page",
            "Unknown"
        )

        text = result[
            "text"
        ]

        context_parts.append(
            f"[Page {page}]\n{text}"
        )

    context = "\n\n".join(
        context_parts
    )

    prompt = f"""
You are an AWS Solutions Architect Associate
(SAA-C02) study assistant.

Answer the user's question using ONLY
the study-guide context below.

Do not invent information.

If the context does not contain enough
information to answer the question, say:

"The study guide does not provide enough
information to answer this question."

Explain the answer clearly and simply.

Use bullet points when useful.

At the end, mention the relevant page
numbers.

STUDY GUIDE CONTEXT
===================

{context}

===================

USER QUESTION
=============

{question}
"""

    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful AWS SAA-C02 "
                    "study assistant. Answer using "
                    "the supplied study-guide context."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response[
        "message"
    ][
        "content"
    ]


# ============================================================
# LOAD DATABASE
# ============================================================

try:

    index, chunks, metadata = (
        load_database()
    )

except Exception as e:

    st.error(
        f"Could not load vector database:\n\n{e}"
    )

    st.stop()


# ============================================================
# DATABASE VALIDATION
# ============================================================

if index.ntotal == 0:

    st.error(
        "FAISS index contains zero vectors."
    )

    st.stop()


if len(chunks) == 0:

    st.error(
        "No document chunks were found."
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📊 Database")

    st.write(
        f"**PDF chunks:** {len(chunks)}"
    )

    st.write(
        f"**FAISS vectors:** {index.ntotal}"
    )

    st.write(
        f"**Vector dimension:** {index.d}"
    )

    st.divider()

    st.write(
        "**Embedding:** "
        f"{EMBEDDING_MODEL}"
    )

    st.write(
        "**LLM:** "
        f"{CHAT_MODEL}"
    )


# ============================================================
# USER INTERFACE
# ============================================================

st.title(
    "📚 AWS SAA-C02 Study Assistant"
)

st.write(
    "Ask questions about your SAA-C02 "
    "study guide."
)

st.success(
    f"Loaded {index.ntotal} vectors."
)


# ============================================================
# QUESTION INPUT
# ============================================================

question = st.text_input(
    "Enter your question:",
    placeholder=(
        "Example: What is Amazon S3 "
        "and when should I use it?"
    )
)


# ============================================================
# ASK QUESTION
# ============================================================

if st.button(
    "🔍 Ask Question",
    type="primary"
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

        st.stop()

    try:

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        with st.spinner(
            "Searching the study guide..."
        ):

            results = search_database(
                question,
                index,
                chunks,
                metadata,
                top_k=5
            )

        if not results:

            st.warning(
                "No relevant information found."
            )

            st.stop()

        # ----------------------------------------------------
        # Generate answer
        # ----------------------------------------------------

        with st.spinner(
            "Generating answer with Ollama..."
        ):

            answer = generate_answer(
                question,
                results
            )

        # ----------------------------------------------------
        # Answer
        # ----------------------------------------------------

        st.subheader(
            "💡 Answer"
        )

        st.markdown(
            answer
        )

        # ----------------------------------------------------
        # Sources
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            "📖 Sources"
        )

        pages = sorted(
            set(
                result[
                    "metadata"
                ].get(
                    "page",
                    "Unknown"
                )
                for result in results
            )
        )

        st.write(
            "Relevant pages: "
            + ", ".join(
                str(page)
                for page in pages
            )
        )

        # ----------------------------------------------------
        # Retrieved chunks
        # ----------------------------------------------------

        with st.expander(
            "🔎 View retrieved sections"
        ):

            for i, result in enumerate(
                results,
                start=1
            ):

                page = result[
                    "metadata"
                ].get(
                    "page",
                    "Unknown"
                )

                score = result[
                    "score"
                ]

                st.markdown(
                    f"### Result {i}"
                )

                st.write(
                    f"**Page:** {page}"
                )

                st.write(
                    f"**Similarity:** "
                    f"{score:.3f}"
                )

                st.write(
                    result["text"]
                )

                st.divider()

    except Exception as e:

        st.error(
            f"An error occurred:\n\n{e}"
        )