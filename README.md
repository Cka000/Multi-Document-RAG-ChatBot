# Multi Document RAG ChatBot

A Retrieval-Augmented Generation (RAG) chatbot built using **LangChain**, **FAISS**, **Hugging Face Embeddings**, **Groq LLM**, and **Streamlit**.

The chatbot indexes multiple documents from the `data/` folder and answers questions using only the information available in those documents.

---

## Features

- Multi-document Retrieval Augmented Generation (RAG)
- Supports multiple file formats
- Semantic search using FAISS
- Hugging Face sentence embeddings
- Groq LLM integration
- Streamlit chat interface
- Multiple LLM selection
- View retrieved document chunks
- Download chat history

---

## Tech Stack

- Python
- Streamlit
- LangChain
- FAISS
- HuggingFace Embeddings (`all-MiniLM-L6-v2`)
- Groq API

---

## Supported File Formats

Place your documents inside the `data/` folder.

Supported formats:

- PDF (`.pdf`) _(text-based PDFs)_
- DOCX (`.docx`)
- TXT (`.txt`)

Example:

```text
data/
│── Python.pdf
│── Java.docx
│── C++.txt
│── DBMS.pdf
```

---

## How to Use

1. Clone the repository.

```bash
git clone <repository-url>
```

2. Install the required packages.

```bash
pip install -r requirements.txt
```

3. Add your Groq API key to a `.env` file.

```text
GROQ_API_KEY=your_api_key_here
```

4. Place your documents inside the `data/` folder.

5. Run the application.

```bash
streamlit run main.py
```

6. Ask questions about your documents.

---

## Note

- The chatbot answers **only from the indexed documents**.
- If the answer is not found in the documents, it will respond accordingly.
- **Scanned or image-based PDFs are not supported** because they require OCR. Use text-based PDFs for best results.

---

## Application Preview

![Multi Document RAG ChatBot](assets/screenshot.png)

---
