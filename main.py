import os
from dotenv import load_dotenv

import streamlit as st

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

load_dotenv()

st.set_page_config(
    page_title="Multi Document RAG ChatBot",
    layout="wide"
)

st.title("Multi Document RAG ChatBot")

st.info("""
To add more knowledge:

1. Put your PDF, DOCX or TXT files inside the **data/** folder.
2. Restart the application.
3. The chatbot will automatically index the new documents.
""")


model = st.sidebar.selectbox(
    "Choose LLM",
    [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "groq/compound-mini",
        "qwen/qwen3-32b"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info("""
Supported Files

• PDF

• DOCX

• TXT
""")

@st.cache_resource
def create_vector_db():

    documents = []

    data_folder = "data"

    if not os.path.exists(data_folder):
        return None, 0, 0

    for file in sorted(os.listdir(data_folder)):

        path = os.path.join(data_folder, file)

        try:

            if file.endswith(".pdf"):
                loader = PyPDFLoader(path)

            elif file.endswith(".docx"):
                loader = Docx2txtLoader(path)

            elif file.endswith(".txt"):
                loader = TextLoader(path, encoding="utf-8")

            else:
                continue

            docs = loader.load()
            text = "".join(doc.page_content for doc in docs).strip()

            print(f"{file} -> Extracted {len(text)} characters")

            print(f"{file} -> {len(docs)} document(s)")

            documents.extend(docs)

        except Exception as e:
            st.warning(f"Couldn't load {file}\n\n{e}")

    if not documents:
        return None, 0, 0

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_db = FAISS.from_documents(
        chunks,
        embeddings
    )

    return vector_db, len(documents), len(chunks)

vector_db, total_docs, total_chunks = create_vector_db()

if vector_db is None:

    st.error("No documents found inside the data folder.")

    st.stop()

st.sidebar.success(f"Documents : {total_docs}")
st.sidebar.success(f"Chunks : {total_chunks}")

retriever = vector_db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k":5,
        "fetch_k":20
    }
)


llm = ChatGroq(
    model_name=model,
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)


prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an intelligent AI assistant.

Answer ONLY using the provided context.

Rules:
1. Answer only from the retrieved context.
2. Do not make up information.
3. If the answer is not found in the context, reply exactly:

Sorry, I couldn't find the answer in the provided documents.

Context:
{context}

Question:
{question}

Answer:
"""
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


question = st.chat_input("Ask a question...")

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.spinner("Searching documents..."):

        docs = retriever.invoke(question)

        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

        final_prompt = prompt.format(
            context=context,
            question=question
        )

        response = llm.invoke(final_prompt)

        answer = response.content

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )



    with st.expander("Retrieved Chunks"):

        st.write(f"Retrieved **{len(docs)}** chunks")

        for i, doc in enumerate(docs, start=1):

            st.markdown(f"### Chunk {i}")

            st.write(doc.page_content)

            st.markdown(
                f"**Source:** `{doc.metadata.get('source','Unknown')}`"
            )

            st.divider()


st.sidebar.markdown("---")

if st.sidebar.button("Clear Chat"):

    st.session_state.messages = []

    st.rerun()

conversation = ""

for msg in st.session_state.messages:

    role = msg["role"].capitalize()

    conversation += f"{role}: {msg['content']}\n\n"

if conversation:

    st.sidebar.download_button(
        label="Download Chat",
        data=conversation,
        file_name="chat_history.txt",
        mime="text/plain"
    )

st.sidebar.markdown("---")

st.sidebar.success(f"Using Model:\n{model}")
