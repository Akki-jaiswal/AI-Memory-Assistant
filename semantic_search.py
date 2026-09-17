import sqlite3
import datetime
import numpy as np
from sentence_transformers import SentenceTransformer

def cosine_similarity(vec_a, vec_b):
    """Calculates how similar two vectors are (1.0 = identical meaning)."""
    # Dot product divided by the magnitude of both vectors
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))

def semantic_search(query, top_k=3, silent=False):
    if not silent:
        print(f"\n🧠 Semantic Search for: '{query}'")
        print("Loading AI Model...")
        
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    query_vector = embedder.encode(query)
    
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, app_name, window_title, filepath, embedding, ocr_text FROM frames WHERE embedding IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        if not silent: print("No memories found!")
        return []
        
    results = []
    for row in rows:
        timestamp, app, title, filepath, embedding_bytes, ocr_text = row
        saved_vector = np.frombuffer(embedding_bytes, dtype=np.float32)
        score = cosine_similarity(query_vector, saved_vector)
        
        if query.lower() in title.lower() or query.lower() in ocr_text.lower():
            score += 1.0  
            
        # We now return ocr_text as well so the LLM can read it!
        results.append((score, timestamp, app, title, filepath, ocr_text))
    
    results.sort(key=lambda x: x[0], reverse=True)
    top_results = results[:top_k]
    
    if not silent:
        print("🏆 Top Matches:")
        print("=" * 50)
        for i in range(len(top_results)):
            score, timestamp, app, title, filepath, _ = top_results[i]
            import datetime
            human_time = datetime.datetime.fromtimestamp(timestamp).strftime('%I:%M:%S %p')
            match_percentage = round(score * 100, 1)
            print(f"[{match_percentage}% Match] 🕒 {human_time}")
            print(f"📱 {app} | {title}")
            print(f"🖼️ File: {filepath}")
            print("-" * 50)
            
    return top_results

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Welcome to your AI Memory Assistant (Search Only)!")
    print("="*50)
    
    while True:
        user_query = input("\n🔍 What are you looking for? (or type 'exit' to quit): ")
        if user_query.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        if user_query.strip():
            semantic_search(user_query)
