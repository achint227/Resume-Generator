import os
import sqlite3
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuration - auto-detect database type based on DATABASE_URL presence
DB_URL = os.environ.get("DATABASE_URL")
DB_PATH = Path(__file__).parent.parent.parent / "resumes.db"
USE_MONGODB = DB_URL is not None and DB_URL.strip() != ""

# Lazy import MongoDB dependencies only if DATABASE_URL is set
if USE_MONGODB:
    import pymongo
    from bson.objectid import ObjectId
    
    myclient = pymongo.MongoClient(DB_URL)
    db = myclient["Resume"]
    collection = db["Resume"]


# SQLite implementation
def _sqlite_get_connection():
    """Get a SQLite connection and ensure table exists"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            data TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_name ON resumes(name)
    """)
    conn.commit()
    return conn


def all_resumes():
    """Get all resumes"""
    if USE_MONGODB:
        res = []
        for doc in collection.find():
            doc["_id"] = str(doc["_id"])
            res.append(doc)
        return res
    else:
        conn = _sqlite_get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, data FROM resumes")
        
        res = []
        for row in cursor.fetchall():
            resume = json.loads(row["data"])
            resume["_id"] = str(row["id"])
            res.append(resume)
        
        conn.close()
        return res


def find_by_id(id):
    """Find resume by ID"""
    if USE_MONGODB:
        document_id = ObjectId(id)
        return collection.find_one({"_id": document_id})
    else:
        conn = _sqlite_get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, data FROM resumes WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            resume = json.loads(row["data"])
            resume["_id"] = row["id"]
            return resume
        return None


def find_by_name(name):
    """Find resume by user name (basic_info.name)"""
    if USE_MONGODB:
        return collection.find({"basic_info.name": name})[0]
    else:
        conn = _sqlite_get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, data FROM resumes")
        
        for row in cursor.fetchall():
            resume = json.loads(row["data"])
            if resume.get("basic_info", {}).get("name") == name:
                resume["_id"] = row["id"]
                conn.close()
                return resume
        
        conn.close()
        raise IndexError("Resume not found")


def find_by_resume_name(name):
    """Find resume by resume name"""
    if USE_MONGODB:
        return collection.find({"name": name})[0]
    else:
        conn = _sqlite_get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, data FROM resumes WHERE name = ?", (name,))
        row = cursor.fetchone()
        
        if row:
            resume = json.loads(row["data"])
            resume["_id"] = row["id"]
            conn.close()
            return resume
        
        conn.close()
        raise IndexError("Resume not found")


def add_resume(resume):
    """Add a new resume"""
    if USE_MONGODB:
        return collection.insert_one(resume).inserted_id
    else:
        conn = _sqlite_get_connection()
        cursor = conn.cursor()
        
        name = resume.get("name")
        data = json.dumps(resume)
        
        cursor.execute("INSERT INTO resumes (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        resume_id = cursor.lastrowid
        conn.close()
        
        return resume_id


def update_resume(id, resume):
    """Update an existing resume"""
    if USE_MONGODB:
        document_id = ObjectId(id)
        result = collection.update_one({"_id": document_id}, {"$set": resume})
        return result.modified_count > 0
    else:
        conn = _sqlite_get_connection()
        cursor = conn.cursor()
        
        name = resume.get("name")
        data = json.dumps(resume)
        
        cursor.execute("UPDATE resumes SET name = ?, data = ? WHERE id = ?", (name, data, id))
        conn.commit()
        modified = cursor.rowcount > 0
        conn.close()
        
        return modified
