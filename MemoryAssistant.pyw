import threading
import capture
import ui

def start_capture_service():
    """Runs the background recording loop."""
    print("Starting background capture service...")
    capture.main()

def start_ui_service():
    """Runs the system tray and popup UI."""
    print("Starting UI service...")
    ui.run_ui()

if __name__ == "__main__":
    # We run the background capture loop in a separate thread so it doesn't block the UI
    capture_thread = threading.Thread(target=start_capture_service, daemon=True)
    capture_thread.start()
    
    # We MUST run the UI (Tkinter) in the main thread, otherwise Windows will crash the app
    start_ui_service()
