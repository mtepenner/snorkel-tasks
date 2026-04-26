from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from collections import Counter
import PyPDF2
import io
import os

app = FastAPI()

# Allow CORS for local GUI testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the static GUI file
os.makedirs("/app/workspace/src/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="/app/workspace/src/static"), name="static")

@app.post("/extract")
async def extract_metadata(file: UploadFile = File(...)):
    content = await file.read()
    reader = PyPDF2.PdfReader(io.BytesIO(content))
    
    # 1. Extract standard metadata
    meta = reader.metadata
    author = meta.author if meta and meta.author else "Unknown Author"
    title = meta.title if meta and meta.title else "Untitled"
    
    # 2. Extract and chunk text for >50k token handling
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + " "
            
    # Simple chunking simulation (e.g., 1000 words per chunk)
    words = full_text.split()
    chunk_size = 1000
    chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
    
    # 3. Extract topics via word-frequency analysis over the parsed text chunks
    stopwords = {
        "the","a","an","to","of","and","is","in","it","for","that","on","at",
        "by","this","with","from","as","are","was","be","or","its","we","our",
        "if","but","not","have","has","had","more","than","their","they","into",
        "which","when","also","been","some","all","new","will","can","do","each",
    }
    word_freq = Counter(
        w.lower() for w in words if w.isalpha() and len(w) > 3 and w.lower() not in stopwords
    )
    keywords = [w for w, _ in word_freq.most_common(10)]
        
    return {
        "filename": file.filename,
        "author": author,
        "title": title,
        "topics": keywords,
        "total_words": len(words),
        "total_chunks": len(chunks)
    }
