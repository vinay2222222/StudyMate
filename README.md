# StudyMate: An AI-Powered PDF-Based Q&A System for Students

## Overview
StudyMate is an AI-driven academic assistant designed to help students interact with their study materials (e.g., lecture notes, textbooks, research papers) through a conversational question-answering interface. Instead of manually searching through large PDF documents, students can upload them and ask natural-language questions. The system provides context-grounded answers with traceable source references, enhancing self-paced learning, research, and exam preparation.

## Features
- **Multi-PDF Upload**: Drag and drop multiple academic PDFs into the interface.
- **Semantic Search**: Utilizes embeddings and vector similarity to retrieve relevant text chunks.
- **Context-Aware Answers**: Generates responses strictly from uploaded documents.
- **Traceable References**: Displays exact source paragraphs for transparency.
- **Session History**: Saves all Q&A pairs for review, downloadable as a text file.
- **Interactive Interface**: Built with a modern Streamlit-based frontend for a responsive experience.

## User Scenarios
- **Concept Clarification**: Get instant explanations for difficult concepts from lecture notes.
- **Studying from Textbooks**: Ask topic-specific questions directly from uploaded textbooks.
- **Viva/Open-Book Test Prep**: Self-test by asking multiple questions and saving answers.
- **Multi-PDF Research**: Query across several research papers for thematic insights.

## Technology Stack/Architecture:
- **Frontend:**
 Streamlit (UI for upload, Q&A, history, transcript).
- **Backend:**
 PyMuPDF (PDF parsing & text extraction).
 SentenceTransformers (all-MiniLM-L6-v2) for embeddings.
 FAISS (semantic search over chunks).
 Hugging Face Transformers (mistralai/Mixtral-8x7B-Instruct-v0.1) for LLM-based answers.
- **Data Persistence:**
 Session state (Q&A history)
 Downloadable transcript (.txt).

## Installation

### Prerequisites
- Python 3.10
- Node.js (for frontend, if applicable)
- Git

### Setup Instructions
## 🔹 1. Clone the Repository
```bash
git clone https://github.com/PuneethKrishnaS/StudyMate.git
cd StudyMate
```

## 🔹 2. Create and Activate Conda Environment
```bash
conda create -n studymate python=3.10 -y
conda activate studymate
```

## 🔹 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If you don’t have `requirements.txt`, install manually:
```bash
pip install streamlit flask pymupdf sentence-transformers faiss-cpu huggingface_hub python-dotenv requests
```

## 🔹 4. Configure Environment Variables
Create a `.env` file in the **root folder** and add:
```ini
HF_API_KEY="your_huggingface_token_here"
MODEL_ID="mistralai/Mixtral-8x7B-Instruct-v0.1"
```
👉 Replace `your_huggingface_token_here` with your Hugging Face token.

## 🔹 5. Run the Backend (Flask API)
```bash
python Backend/app.py
```
- This starts Flask backend on **http://127.0.0.1:8000**

⚠️ If you get signal errors, edit `Backend/app.py`:
```python
app.run(host="127.0.0.1", port=8000, debug=False, use_reloader=False)
```

## 🔹 6. Run the Frontend (Streamlit UI)
In a **new Anaconda Prompt window**:
```bash
conda activate studymate
streamlit run Frontend/app.py
```
- This starts frontend on **http://localhost:8501**

## 🔹 7. Use StudyMate
- Upload PDFs in the web app  
- Ask natural language questions  
- Get AI-powered answers with source references  

## 🔹 8. Project Structure
```
StudyMate/
│── Backend/        # Flask backend
│    └── app.py
│
│── Frontend/       # Streamlit frontend
│    └── app.py
│
│── requirements.txt
│── .env
```

## 🔹 9. Troubleshooting
- **ModuleNotFoundError** → install missing package:
  ```bash
  pip install <package_name>
  ```
- **FAISS error on Windows** → install CPU version:
  ```bash
  pip install faiss-cpu
  ```
- **HuggingFace API error** → check `.env` file and token validity.

---

✅ Now you can run StudyMate easily inside **Anaconda Prompt** with backend + frontend working together!
