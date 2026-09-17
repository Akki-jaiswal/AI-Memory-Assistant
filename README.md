# 🧠 AI Memory Assistant (for Windows)

<div align="center">
  <i>A 100% private, offline, open-source alternative to Rewind.ai and Microsoft Recall.</i>
</div>

<br>

## 🌟 What is this?
Have you ever closed a tab and immediately forgotten what you were reading? Or lost a piece of code you wrote 4 hours ago? 

**AI Memory Assistant** is a "Search Engine for your Life." It silently runs in the background of your Windows machine, compressing and saving what you see on your screen. When you need to remember something, you simply type a concept (e.g. "youtube video about black holes" or "database error"), and the AI instantly pulls up the exact timestamp, application, and screenshot of your past work.

## 🔒 The Privacy Guarantee
Unlike commercial alternatives, **this app respects your privacy.**
* **100% Local:** Everything runs entirely on your device.
* **No Cloud APIs:** Your screenshots and text never leave your hard drive.
* **No Subscriptions:** Completely free and open-source.

## 🎯 Who is this for?
* **Developers & Engineers:** Instantly search your past terminal errors, lost code snippets, and API documentation you read hours ago.
* **Researchers & Students:** Never lose a PDF quote or a Wikipedia article again. 
* **ADHD & Productivity:** Stop worrying about organizing bookmarks. Just let the assistant remember it for you.

---

## 🚀 One-Click Installation

We designed this to be completely frictionless for non-technical users. 

### Step 1: Download
Click the button below to download the app directly to your computer:

<a href="https://github.com/Akki-jaiswal/AI-Memory-Assistant/archive/refs/heads/main.zip">
  <img src="https://img.shields.io/badge/Download_Application_ZIP-0072C6?style=for-the-badge&logo=windows&logoColor=white" alt="Download ZIP" />
</a>

### Step 2: Install
1. Extract the downloaded ZIP file.
2. Open the folder and double-click the **`install.bat`** file.
3. The script will automatically install the required AI libraries and launch the application silently in the background!

## 💡 How to Use
1. Look at your Windows Taskbar (in the bottom right corner near your clock).
2. You will see a sleek **AI Logo**.
3. Double-click the icon to open the Search Popup.
4. Type what you are looking for and hit Enter!
5. **Pro-tip:** Click any screenshot in the search results to zoom in and view it at full 1080p resolution!

---

## ⚙️ How it Works (Under the Hood)
For the engineers, here is the architecture of the engine:
* **Capture Engine:** Uses `mss` and Perceptual Hashing (`imagehash`) to efficiently capture only unique frames, saving massive storage space.
* **OCR Engine:** Uses `rapidocr-onnxruntime` to extract text from your screen offline.
* **Semantic Search:** Uses `sentence-transformers` to convert your screen text into dense vector embeddings, allowing you to search by *concept* rather than exact keywords.
* **UI:** Native Windows GUI using `tkinter` and `pystray`.
