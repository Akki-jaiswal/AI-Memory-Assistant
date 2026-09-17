import time
import os
import mss
import cv2
import numpy as np
import imagehash
from PIL import Image
import sqlite3
import win32gui
import win32process
import psutil
from rapidocr_onnxruntime import RapidOCR
from sentence_transformers import SentenceTransformer

# Create a directory to store our frames
SAVE_DIR = "frames"
os.makedirs(SAVE_DIR, exist_ok=True)

# Threshold for image difference (0 means perfectly identical)
HASH_DIFFERENCE_THRESHOLD = 2 
CAPTURE_INTERVAL_SECONDS = 2

def init_db():
    """Initialize the SQLite database to store our metadata."""
    conn = sqlite3.connect("memory.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS frames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            filepath TEXT,
            app_name TEXT,
            window_title TEXT,
            ocr_text TEXT
        )
    """)
    
    # Try to add the new embedding column (if it doesn't already exist from Phase 2)
    try:
        cursor.execute("ALTER TABLE frames ADD COLUMN embedding BLOB")
    except sqlite3.OperationalError:
        pass # Column already exists
        
    conn.commit()
    return conn

def get_active_window_info():
    """Gets the title and app name of the currently active window on Windows."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        
        # Get the process ID from the window handle
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        app_name = process.name()
        
        return window_title, app_name
    except Exception:
        return "Unknown", "Unknown"

def get_image_hash(cv2_image):
    """Convert OpenCV image to PIL Image and calculate perceptual hash."""
    # Convert BGRA (mss/OpenCV format) to RGB
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGRA2RGB)
    pil_image = Image.fromarray(rgb_image)
    return imagehash.phash(pil_image)

def main():
    print("Starting AI Memory Assistant Capture...")
    print(f"Saving unique frames to: {os.path.abspath(SAVE_DIR)}")
    
    # Initialize the database
    db_conn = init_db()
    db_cursor = db_conn.cursor()
    
    # Initialize the OCR Engine
    ocr_engine = RapidOCR()
    
    # --- NEW: Initialize the Semantic Embedding Model ---
    print("Loading AI Embedding Model (this takes a few seconds on startup)...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded. Ready to capture.")
    
    last_hash = None
    
    # Initialize the screen capture object (Fixed DeprecationWarning here!)
    with mss.MSS() as sct:
        # Get the primary monitor
        monitor = sct.monitors[1] 
        
        while True:
            try:
                # 1. Capture the screen
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                
                # 2. Calculate the perceptual hash
                current_hash = get_image_hash(frame)
                
                # 3. Compare with the previous frame
                is_unique = False
                if last_hash is None:
                    is_unique = True
                else:
                    difference = current_hash - last_hash
                    if difference > HASH_DIFFERENCE_THRESHOLD:
                        is_unique = True
                
                # 4. If the screen changed, save it and record metadata
                if is_unique:
                    timestamp = int(time.time())
                    filename = os.path.join(SAVE_DIR, f"frame_{timestamp}.webp")
                    
                    # Compress and save image
                    cv2.imwrite(filename, frame, [cv2.IMWRITE_WEBP_QUALITY, 50])
                    
                    # --- NEW: Get Active Window Metadata ---
                    window_title, app_name = get_active_window_info()
                    
                    # --- NEW: Run OCR to extract text from the screen ---
                    ocr_result, _ = ocr_engine(frame)
                    extracted_text = ""
                    
                    if ocr_result:
                        text_lines = [line[1] for line in ocr_result]
                        extracted_text = "\n".join(text_lines)
                        
                    # --- NEW: Generate AI Semantic Embedding ---
                    # We combine the window title and OCR text to give the AI full context
                    context_for_ai = f"App: {app_name}. Title: {window_title}. Text: {extracted_text}"
                    
                    # Convert the text into a vector (array of numbers) and convert to bytes for SQLite
                    embedding_vector = embedder.encode(context_for_ai)
                    embedding_bytes = embedding_vector.tobytes()
                    
                    # --- UPDATED: Save everything to Database (including embedding) ---
                    db_cursor.execute(
                        "INSERT INTO frames (timestamp, filepath, app_name, window_title, ocr_text, embedding) VALUES (?, ?, ?, ?, ?, ?)",
                        (timestamp, filename, app_name, window_title, extracted_text, embedding_bytes)
                    )
                    db_conn.commit()
                    
                    diff_score = current_hash - last_hash if last_hash else 'First frame'
                    print(f"Saved: {app_name[:15]}... | OCR: {len(extracted_text)} chars | Vectorized!")
                    
                    last_hash = current_hash
                
                # 5. Wait before capturing the next frame
                time.sleep(CAPTURE_INTERVAL_SECONDS)
                
            except KeyboardInterrupt:
                print("\nStopping capture loop.")
                break
            except Exception as e:
                print(f"Error during capture: {e}")
                time.sleep(CAPTURE_INTERVAL_SECONDS)
    
    db_conn.close()

if __name__ == "__main__":
    main()
