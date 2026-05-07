from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
import sqlite3
import string
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "urls.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

class URLRequest(BaseModel):
    url: str

def generate_id(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.post("/shorten")
def shorten_url(request: URLRequest):
    short_id = generate_id()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO urls (id, url) VALUES (?, ?)",
        (short_id, request.url)
    )
    conn.commit()
    conn.close()

    return {
        "short_url": f"http://localhost:8000/{short_id}"
    }

@app.get("/{short_id}")
def redirect_url(short_id: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM urls WHERE id = ?", (short_id,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        raise HTTPException(status_code=404, detail="URL no encontrada")

    return RedirectResponse(result[0])