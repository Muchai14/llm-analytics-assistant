# LLM Analytics Assistant

Ask questions about a database in plain English. The system uses an LLM to convert natural language into SQL, executes the query, and returns the result.

## How it works

1. User types a question in plain English (e.g. "What is the total revenue?")
2. The system retrieves relevant data context using RAG (ChromaDB vector store)
3. The LLM generates a SQL query based on the database schema and retrieved context
4. The SQL query is executed against a SQLite database
5. The result is returned to the user

## Tech stack

- Python
- FastAPI (web framework)
- Groq API (LLM inference)
- ChromaDB (vector store for RAG)
- SQLite (database)
- HTML/JavaScript (frontend)

## Features

- Natural language to SQL conversion
- RAG pipeline for context-aware query generation
- Error handling: returns an error instead of hallucinating data when a question cannot be answered
- Simple web UI for non-technical users

## Setup

1. Clone this repo
2. Install dependencies:
   pip install fastapi uvicorn groq chromadb
3. Set your Groq API key:
   export GROQ_API_KEY="your_key_here"
4. Create the database:
   python3 setup_db.py
5. Start the server:
   uvicorn api:app --reload
6. Open http://127.0.0.1:8000 in your browser

## Example questions

- What is the total revenue?
- Which product has the highest total sales?
- How many orders did customer 101 place?
- What is the average order amount?

## Error handling

If a question cannot be answered with the available data, the system returns an error instead of inventing data.
