import sqlite3
import chromadb

# Connect to database
conn = sqlite3.connect('demo.db')

# Initialize ChromaDB client (in-memory for simplicity)
chroma_client = chromadb.Client()

# Create or get a collection
collection = chroma_client.get_or_create_collection(name="orders_context")

def build_context():
    """Extract data summaries from the database and store them as embeddings"""
    # Clear existing collection
    global collection
    chroma_client.delete_collection(name="orders_context")
    collection = chroma_client.get_or_create_collection(name="orders_context")

    # Get all rows from orders
    rows = conn.execute("SELECT * FROM orders").fetchall()

    # Convert each row into a text description
    documents = []
    ids = []
    for i, row in enumerate(rows):
        order_id, customer_id, product, amount, order_date = row
        text = f"Order {order_id}: customer {customer_id} bought {product} for ${amount} on {order_date}."
        documents.append(text)
        ids.append(f"order_{order_id}")

    # Add to ChromaDB
    collection.add(documents=documents, ids=ids)
    print(f"Added {len(documents)} documents to the vector store.")

def retrieve_context(question: str, n_results: int = 3):
    """Retrieve relevant context from the vector store based on the question"""
    results = collection.query(query_texts=[question], n_results=n_results)
    return results['documents'][0] if results['documents'] else []

if __name__ == "__main__":
    # Build the vector store
    build_context()

    # Test retrieval
    question = "Which product has the highest sales?"
    context = retrieve_context(question)
    print(f"\nQuestion: {question}")
    print("Retrieved context:")
    for doc in context:
        print(f"  - {doc}")
