import os
import sqlite3
from groq import Groq

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Connect to database
conn = sqlite3.connect('demo.db')

# Define schema so the model knows what tables exist
SCHEMA = """
Table: orders
Columns:
  order_id (INTEGER)
  customer_id (INTEGER)
  product (TEXT)
  amount (REAL)
  order_date (TEXT)
"""

def nl_to_sql(question):
    """Convert natural language question to SQL"""
    prompt = f"""You are a SQL expert. Given this database schema:
{SCHEMA}

Write a SQL query to answer this question: {question}

Rules:
- Return ONLY the SQL query, no explanation, no markdown, no backticks.
- Use standard SQLite syntax.
- Always end with a semicolon.
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def ask(question):
    """Full pipeline: natural language -> SQL -> execute -> return result"""
    sql = nl_to_sql(question)
    print(f"Generated SQL: {sql}")
    result = conn.execute(sql).fetchall()
    return result

if __name__ == "__main__":
    question = "What is the total revenue?"
    print(f"Question: {question}")
    result = ask(question)
    print(f"Result: {result}")
