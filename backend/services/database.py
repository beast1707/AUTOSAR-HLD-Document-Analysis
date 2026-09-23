import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any
from backend.utils.config import settings
from backend.utils.logging import setup_logger

logger = setup_logger("database")

def get_db_connection():
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # documents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        pages INTEGER,
        status TEXT,
        created_at TEXT
    )
    ''')

    # chunks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chunks (
        id TEXT PRIMARY KEY,
        document_id TEXT,
        page INTEGER,
        section TEXT,
        heading TEXT,
        text TEXT,
        FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
    )
    ''')

    # entities table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entities (
        id TEXT PRIMARY KEY,
        document_id TEXT,
        type TEXT,
        name TEXT,
        description TEXT,
        page INTEGER,
        FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
    )
    ''')

    # chat_history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id TEXT PRIMARY KEY,
        document_id TEXT,
        question TEXT,
        answer TEXT,
        citation_pages TEXT,
        confidence REAL,
        timestamp TEXT,
        FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
    )
    ''')

    # flows table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flows (
        id TEXT PRIMARY KEY,
        document_id TEXT,
        title TEXT,
        purpose TEXT,
        steps TEXT,
        components TEXT,
        citations TEXT,
        confidence REAL,
        timestamp TEXT,
        FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()
    logger.info("SQLite database initialized successfully.")

def save_document(doc_id: str, name: str, pages: int, status: str = "uploaded"):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO documents (id, name, pages, status, created_at) VALUES (?, ?, ?, ?, ?)",
        (doc_id, name, pages, status, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def update_document_status(doc_id: str, status: str):
    conn = get_db_connection()
    conn.execute("UPDATE documents SET status = ? WHERE id = ?", (status, doc_id))
    conn.commit()
    conn.close()

def save_chunk(doc_id: str, page: int, section: str, heading: str, text: str):
    chunk_id = str(uuid.uuid4())
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO chunks (id, document_id, page, section, heading, text) VALUES (?, ?, ?, ?, ?, ?)",
        (chunk_id, doc_id, page, section, heading, text)
    )
    conn.commit()
    conn.close()
    return chunk_id

def save_entity(doc_id: str, type: str, name: str, description: str, page: int):
    entity_id = str(uuid.uuid4())
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO entities (id, document_id, type, name, description, page) VALUES (?, ?, ?, ?, ?, ?)",
        (entity_id, doc_id, type, name, description, page)
    )
    conn.commit()
    conn.close()

def get_entities(doc_id: str = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    query = "SELECT * FROM entities"
    params = ()
    if doc_id:
        query += " WHERE document_id = ?"
        params = (doc_id,)
    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_chat(doc_id: str, question: str, answer: str, citation_pages: str, confidence: float):
    chat_id = str(uuid.uuid4())
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO chat_history (id, document_id, question, answer, citation_pages, confidence, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (chat_id, doc_id, question, answer, citation_pages, confidence, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_chat_history(doc_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM chat_history WHERE document_id = ? ORDER BY timestamp ASC", (doc_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_documents() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM documents ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_flow(doc_id: str, title: str, purpose: str, steps: str, components: str, citations: str, confidence: float):
    flow_id = str(uuid.uuid4())
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO flows (id, document_id, title, purpose, steps, components, citations, confidence, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (flow_id, doc_id, title, purpose, steps, components, citations, confidence, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_flows(doc_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM flows WHERE document_id = ? ORDER BY timestamp ASC", (doc_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_document(doc_id: str):
    conn = get_db_connection()
    conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    # SQLite ON DELETE CASCADE handles related entities if PRAGMA foreign_keys = ON
    conn.commit()
    conn.close()
