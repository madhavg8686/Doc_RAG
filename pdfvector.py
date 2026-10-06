import os
import pickle

import faiss
import numpy as np
import PyPDF2
import ollama


# ============================================================
# FILE PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PDF_FILE = os.path.join(
    BASE_DIR,
    "SAA-C02 study guide .pdf"
)

INDEX_FILE = os.path.join(
    BASE_DIR,
    "vector.index"
)

CHUNKS_FILE = os.path.join(
    BASE_DIR,
    "chunks.pkl"
)


# ============================================================
# OLLAMA SETTINGS
# ============================================================

EMBEDDING_MODEL = "nomic-embed-text"


# ============================================================
# TEST OLLAMA
# ============================================================

def test_ollama():

    print("=" * 60)
    print("TESTING OLLAMA")
    print("=" * 60)

    try:

        response = ollama.embed(
            model=EMBEDDING_MODEL,
            input="AWS S3"
        )

        embedding = response["embeddings"][0]

        print(
            "Ollama embedding test successful."
        )

        print(
            f"Embedding dimension: "
            f"{len(embedding)}"
        )

    except Exception as e:

        raise RuntimeError(
            "Could not connect to Ollama.\n\n"
            "Make sure Ollama is running and "
            "that you installed:\n\n"
            "ollama pull nomic-embed-text\n\n"
            f"Original error:\n{e}"
        )


# ============================================================
# EXTRACT PDF TEXT
# ============================================================

def extract_pdf():

    print("=" * 60)
    print("READING PDF")
    print("=" * 60)

    if not os.path.exists(PDF_FILE):

        raise FileNotFoundError(
            f"PDF not found:\n{PDF_FILE}"
        )

    print(
        f"PDF: {PDF_FILE}"
    )

    with open(
        PDF_FILE,
        "rb"
    ) as f:

        reader = PyPDF2.PdfReader(f)

        total_pages = len(
            reader.pages
        )

        print(
            f"Total pages: {total_pages}"
        )

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            print(
                f"Reading page "
                f"{page_number}/{total_pages}"
            )

            text = page.extract_text() or ""

            text = " ".join(
                text.split()
            )

            if text:

                pages.append({
                    "text": text,
                    "page": page_number
                })

    return pages, total_pages


# ============================================================
# CREATE CHUNKS
# ============================================================

def create_chunks(
    pages,
    chunk_size=500
):

    print("=" * 60)
    print("CREATING CHUNKS")
    print("=" * 60)

    chunks = []
    metadata = []

    for page in pages:

        text = page["text"]
        page_number = page["page"]

        for start in range(
            0,
            len(text),
            chunk_size
        ):

            chunk = text[
                start:start + chunk_size
            ].strip()

            if not chunk:
                continue

            chunks.append(chunk)

            metadata.append({
                "page": page_number,
                "start": start,
                "end": min(
                    start + chunk_size,
                    len(text)
                )
            })

    print(
        f"Created {len(chunks)} chunks."
    )

    if not chunks:

        raise ValueError(
            "No chunks were created. "
            "The PDF may not contain extractable text."
        )

    return chunks, metadata


# ============================================================
# CREATE OLLAMA EMBEDDINGS
# ============================================================

def create_embeddings(chunks):

    print("=" * 60)
    print("CREATING OLLAMA EMBEDDINGS")
    print("=" * 60)

    embeddings = []

    total = len(chunks)

    for i, chunk in enumerate(chunks):

        print(
            f"Processing "
            f"{i + 1}/{total}"
        )

        try:

            response = ollama.embed(
                model=EMBEDDING_MODEL,
                input=chunk
            )

            embedding = response[
                "embeddings"
            ][0]

            embeddings.append(
                embedding
            )

        except Exception as e:

            raise RuntimeError(
                f"Failed while embedding "
                f"chunk {i + 1}.\n\n"
                f"Error: {e}"
            )

    embeddings = np.array(
        embeddings,
        dtype="float32"
    )

    print(
        f"Embedding shape: "
        f"{embeddings.shape}"
    )

    return embeddings


# ============================================================
# CREATE FAISS INDEX
# ============================================================

def create_faiss_index(
    embeddings
):

    print("=" * 60)
    print("CREATING FAISS INDEX")
    print("=" * 60)

    # Normalize vectors for cosine similarity
    faiss.normalize_L2(
        embeddings
    )

    dimension = embeddings.shape[1]

    print(
        f"Vector dimension: "
        f"{dimension}"
    )

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    print(
        f"Vectors added: "
        f"{index.ntotal}"
    )

    return index


# ============================================================
# SAVE DATABASE
# ============================================================

def save_database(
    index,
    chunks,
    metadata,
    total_pages
):

    print("=" * 60)
    print("SAVING DATABASE")
    print("=" * 60)

    # Save FAISS
    faiss.write_index(
        index,
        INDEX_FILE
    )

    # Save chunks
    with open(
        CHUNKS_FILE,
        "wb"
    ) as f:

        pickle.dump(
            {
                "chunks": chunks,
                "metadata": metadata,
                "total_pages": total_pages
            },
            f
        )

    # --------------------------------------------------------
    # Verify files
    # --------------------------------------------------------

    index_size = os.path.getsize(
        INDEX_FILE
    )

    chunks_size = os.path.getsize(
        CHUNKS_FILE
    )

    print(
        f"vector.index size: "
        f"{index_size:,} bytes"
    )

    print(
        f"chunks.pkl size: "
        f"{chunks_size:,} bytes"
    )

    if index_size == 0:

        raise RuntimeError(
            "vector.index is empty."
        )

    # --------------------------------------------------------
    # Test reading FAISS
    # --------------------------------------------------------

    print(
        "Testing saved FAISS index..."
    )

    test_index = faiss.read_index(
        INDEX_FILE
    )

    print(
        "Successfully reopened index."
    )

    print(
        f"Vectors: "
        f"{test_index.ntotal}"
    )

    print(
        f"Dimension: "
        f"{test_index.d}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("AWS SAA-C02 LOCAL RAG DATABASE")
    print("=" * 60)

    # Test Ollama
    test_ollama()

    # Extract PDF
    pages, total_pages = extract_pdf()

    # Create chunks
    chunks, metadata = create_chunks(
        pages,
        chunk_size=500
    )

    # Create embeddings
    embeddings = create_embeddings(
        chunks
    )

    # Create FAISS
    index = create_faiss_index(
        embeddings
    )

    # Save
    save_database(
        index,
        chunks,
        metadata,
        total_pages
    )

    print("\n")
    print("=" * 60)
    print("SUCCESS")
    print("=" * 60)

    print(
        f"Pages: {total_pages}"
    )

    print(
        f"Chunks: {len(chunks)}"
    )

    print(
        f"Vectors: {index.ntotal}"
    )

    print(
        f"Dimension: {index.d}"
    )

    print("=" * 60)


if __name__ == "__main__":

    main()