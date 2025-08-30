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
**Frontend:**
Streamlit (UI for upload, Q&A, history, transcript).
**Backend:**
PyMuPDF (PDF parsing & text extraction).
SentenceTransformers (all-MiniLM-L6-v2) for embeddings.
FAISS (semantic search over chunks).
Hugging Face Transformers (flan-t5-large, bart-base) for LLM-based answers.
**Data Persistence:**
Session state (Q&A history)
Downloadable transcript (.txt).

## Installation

### Prerequisites
- Python 3.10
- Node.js (for frontend, if applicable)
- Git

### Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/vinay2222222/StudyMate.git
   cd StudyMate

# Hugging Face API Configuration
HF_API_KEY="your_hugging_face_api_key_here"

MODEL_ID="mistralai/Mixtral-8x7B-Instruct-v0.1"
