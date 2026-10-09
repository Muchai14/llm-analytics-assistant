import os
import sqlite3
import chromadb
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
conn = sqlite3.connect('demo.db', check_same_thread=False)

SCHEMA = """
Table: orders
Columns:
  order_id (INTEGER)
  customer_id (INTEGER)
  product (TEXT)
  amount (REAL)
  order_date (TEXT)
"""

# Initialize ChromaDB and build context
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="orders_context")

def build_context():
    """Load all rows from orders into the vector store"""
    global collection
    try:
        chroma_client.delete_collection(name="orders_context")
    except Exception:
        pass
    collection = chroma_client.get_or_create_collection(name="orders_context")

    rows = conn.execute("SELECT * FROM orders").fetchall()
    documents = []
    ids = []
    for row in rows:
        order_id, customer_id, product, amount, order_date = row
        text = f"Order {order_id}: customer {customer_id} bought {product} for ${amount} on {order_date}."
        documents.append(text)
        ids.append(f"order_{order_id}")

    if documents:
        collection.add(documents=documents, ids=ids)

def retrieve_context(question: str, n_results: int = 3):
    """Retrieve relevant rows as context"""
    try:
        results = collection.query(query_texts=[question], n_results=n_results)
        return results['documents'][0] if results['documents'] else []
    except Exception:
        return []

# Build context at startup
build_context()

app = FastAPI(title="LLM Analytics Assistant")

class Query(BaseModel):
    question: str

def nl_to_sql(question: str, context: list) -> str:
    """Convert natural language question to SQL using schema + retrieved context"""
    context_text = "\n".join(context) if context else "No additional context."
    prompt = f"""You are a SQL expert. Given this database schema:
{SCHEMA}

Here is some relevant data from the database to help you understand the content:
{context_text}

Write a SQL query to answer this question: {question}

Rules:
- Return ONLY the SQL query, no explanation, no markdown, no backticks.
- Use standard SQLite syntax.
- Always end with a semicolon.
- If the question CANNOT be answered using ONLY the tables and columns in the schema above, return exactly: SELECT 'ERROR: question cannot be answered';
- Do NOT invent data, columns, or tables that are not in the schema.
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>LLM Analytics Assistant</title>
        <style>
            body { font-family: Arial; max-width: 700px; margin: 60px auto; padding: 20px; }
            h1 { color: #333; }
            input { width: 70%; padding: 10px; font-size: 16px; }
            button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
            pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h1>LLM Analytics Assistant</h1>
        <p>Ask a question about the orders database in plain English.</p>
        <input id="question" placeholder="e.g. What is the total revenue?" />
        <button onclick="askQuestion()">Ask</button>
        <div id="output"></div>
        <script>
            async function askQuestion() {
                const q = document.getElementById('question').value;
                const output = document.getElementById('output');
                output.innerHTML = '<p>Loading...</p>';
                const res = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: q})
                });
                const data = await res.json();
                if (data.error) {
                    output.innerHTML = '<p class="error">' + data.error + '</p>' +
                                       '<pre>SQL: ' + data.sql + '</pre>';
                } else {
                    output.innerHTML = '<pre>SQL: ' + data.sql + '</pre>' +
                                       '<pre>Result: ' + JSON.stringify(data.result) + '</pre>';
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/ask")
def ask(q: Query):
    try:
        context = retrieve_context(q.question)
        sql = nl_to_sql(q.question, context)
    except Exception as e:
        return {"error": f"LLM failed to generate SQL: {str(e)}"}

    if "ERROR: question cannot be answered" in sql:
        return {
            "question": q.question,
            "sql": sql,
            "error": "This question cannot be answered with the available data."
        }

    try:
        result = conn.execute(sql).fetchall()
        return {
            "question": q.question,
            "sql": sql,
            "result": result,
            "context_used": context
        }
    except Exception as e:
        return {
            "question": q.question,
            "sql": sql,
            "error": f"SQL execution failed: {str(e)}"
        }
