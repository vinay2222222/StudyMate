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

## Technical Architecture
- **Input Layer**: PDF upload via Streamlit file uploader, text extraction, and chunking with PyMuPDF (500-word chunks, 100-word overlap).
- **Semantic Retrieval Layer**: Embedding model (`all-MiniLM-L6-v2` via SentenceTransformers), vector indexing with FAISS, top-k retrieval (default: k=3).
- **LLM Inference Layer**: Uses Hugging Face’s `mistralai/Mixtral-8x7B-Instruct-v0.1` for factual, concise answers with structured formatting.
- **Data Persistence Layer**: Session history tracked in memory, exportable as `.txt`.
- **Frontend & UI Layer**: Modern Streamlit interface with expandable reference sections and Q&A logs.
- **Configuration & Security Layer**: `.env` file for API credentials, supports easy model configuration.

## Technology Stack
- **Languages & Frameworks**: Python, Streamlit
- **Libraries**: PyMuPDF, SentenceTransformers, FAISS, python-dotenv, huggingface_hub
- **AI Model**: Hugging Face `mistralai/Mixtral-8x7B-Instruct-v0.1`
- **Environment**: Windows 11, Python 3.10, VS Code

## Installation

### Prerequisites
- Python 3.10
- Node.js (for frontend, if applicable)
- Git

### Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/StudyMate.git
   cd StudyMate

# Hugging Face API Configuration
HF_API_KEY="your_hugging_face_api_key_here"
MODEL_ID="mistralai/Mixtral-8x7B-Instruct-v0.1"
