import streamlit as st
import sys
import os
import numpy as np
from datetime import datetime
import io
import json

# Ensure project paths are in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pdf_parser import extract_text_from_pdf, chunk_by_topic
from core.embeddings import get_embeddings
from core.retrieval import (
    create_faiss_index,
    retrieve_top_k,
    save_faiss_index,
    load_faiss_index,
    save_chunks,
    load_chunks
)
from core.llm_integration import generate_answer
from config.settings import TOP_K, UPLOADS_DIR

st.set_page_config(page_title="📚 StudyMate ", layout="wide")

st.title("📚 StudyMate")
st.write("Upload PDFs, ask questions, and get AI answers which help you to learn things easily.")

# Initialize session state for history
if "history" not in st.session_state:
    st.session_state.history = []

# Try loading saved chunks and index
all_chunks = []
index = None
saved_chunks = load_chunks("study_chunks.json")
saved_index = load_faiss_index("study_index.index")

if saved_chunks and saved_index:
    all_chunks = saved_chunks
    index = saved_index
    st.success(f"✅ Loaded {len(all_chunks)} chunks from saved data.")

# Upload PDF files
uploaded_files = st.file_uploader("Upload your PDF(s)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    all_chunks = []
    for file in uploaded_files:
        # Save PDF to uploads folder
        pdf_path = os.path.join(UPLOADS_DIR, file.name)
        with open(pdf_path, "wb") as f:
            f.write(file.getbuffer())

        # Extract and chunk
        text = extract_text_from_pdf(pdf_path)
        chunks = chunk_by_topic(text)
        all_chunks.extend(chunks)

    st.success(f"✅ Processed {len(all_chunks)} topic-based chunks from {len(uploaded_files)} file(s).")

    # Save chunks to disk
    save_chunks(all_chunks, "study_chunks.json")

    # Create and save FAISS index
    embeddings = get_embeddings(all_chunks)
    embeddings_array = np.array(embeddings)
    index = create_faiss_index(embeddings_array)
    save_faiss_index(index, "study_index.index")

# Question input
question = st.text_input("Ask a question about your PDFs:")

if st.button("Get Answer") and question and index:
    # Retrieve relevant chunks
    top_chunks = retrieve_top_k(question, index, all_chunks, TOP_K)

    # Generate answer
    answer = generate_answer(top_chunks, question)

    # Save to history
    st.session_state.history.append({
        "question": question,
        "answer": answer,
        "context": top_chunks,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# Show latest answer
if st.session_state.history:
    latest = st.session_state.history[-1]
    st.markdown(f"### 📖 Answer:\n{latest['answer']}")

    with st.expander("📌 Referenced Context"):
        for i, chunk in enumerate(latest['context'], 1):
            st.write(f"**Chunk {i}:**\n{chunk}")

# Show Q&A history
if st.session_state.history:
    st.markdown("## 📜 Q&A History")
    for entry in reversed(st.session_state.history):
        st.markdown(f"**Q:** {entry['question']}")
        st.markdown(f"**A:** {entry['answer']}")
        st.caption(f"🕒 {entry['timestamp']}")
        st.write("---")

    # Export history as text file
    history_text = ""
    for entry in st.session_state.history:
        history_text += f"Q: {entry['question']}\nA: {entry['answer']}\nTime: {entry['timestamp']}\n\n"

    buf = io.BytesIO(history_text.encode("utf-8"))
    st.download_button(
        label="⬇️ Download Q&A History",
        data=buf,
        file_name="studymate_history.txt",
        mime="text/plain"
    )
