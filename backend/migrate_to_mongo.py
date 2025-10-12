#!/usr/bin/env python3
"""
Script to migrate data from SQLite to MongoDB
"""
import sqlite3
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "specter_legal")

async def migrate_legal_acts():
    """Migrate legal acts from SQLite to MongoDB"""
    print("Starting migration of legal acts...")
    
    # Connect to MongoDB
    mongo_client = AsyncIOMotorClient(MONGODB_URL)
    mongo_db = mongo_client[DATABASE_NAME]
    legal_acts_collection = mongo_db.legal_acts
    
    # Connect to SQLite
    sqlite_path = os.path.join(os.path.dirname(__file__), "..", "legal_acts.db")
    if not os.path.exists(sqlite_path):
        print(f"SQLite database not found at {sqlite_path}")
        return
    
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    
    try:
        # Get all legal acts from SQLite
        cursor.execute("SELECT act, section, title, definition, punishment, keywords FROM laws")
        rows = cursor.fetchall()
        
        if not rows:
            print("No legal acts found in SQLite database")
            return
        
        # Clear existing data in MongoDB
        await legal_acts_collection.delete_many({})
        print(f"Cleared existing legal acts in MongoDB")
        
        # Prepare documents for MongoDB
        documents = []
        for row in rows:
            doc = {
                "act": row[0] or "",
                "section": row[1] or "",
                "title": row[2] or "",
                "definition": row[3] or "",
                "punishment": row[4] or "",
                "keywords": row[5] or ""
            }
            documents.append(doc)
        
        # Insert into MongoDB
        if documents:
            result = await legal_acts_collection.insert_many(documents)
            print(f"Successfully migrated {len(result.inserted_ids)} legal acts to MongoDB")
        
        # Create indexes
        await legal_acts_collection.create_index("act")
        await legal_acts_collection.create_index("section")
        await legal_acts_collection.create_index([("title", "text"), ("definition", "text"), ("keywords", "text")])
        print("Created indexes for legal acts collection")
        
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()
        mongo_client.close()

async def migrate_users():
    """Migrate users from SQLite to MongoDB"""
    print("Starting migration of users...")
    
    # Connect to MongoDB
    mongo_client = AsyncIOMotorClient(MONGODB_URL)
    mongo_db = mongo_client[DATABASE_NAME]
    users_collection = mongo_db.users
    
    # Connect to SQLite
    sqlite_path = os.path.join(os.path.dirname(__file__), "..", "users.db")
    if not os.path.exists(sqlite_path):
        print(f"Users database not found at {sqlite_path}")
        return
    
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    
    try:
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Users table not found in SQLite database")
            return
        
        # Get all users from SQLite
        cursor.execute("SELECT email, password_hash, full_name, is_verified, is_active, created_at FROM users")
        rows = cursor.fetchall()
        
        if not rows:
            print("No users found in SQLite database")
            return
        
        # Clear existing users in MongoDB
        await users_collection.delete_many({})
        print(f"Cleared existing users in MongoDB")
        
        # Prepare documents for MongoDB
        documents = []
        for row in rows:
            doc = {
                "email": row[0],
                "password_hash": row[1],
                "full_name": row[2],
                "is_verified": bool(row[3]) if row[3] is not None else False,
                "is_active": bool(row[4]) if row[4] is not None else True,
                "created_at": row[5] if row[5] else None,
                "updated_at": row[5] if row[5] else None
            }
            documents.append(doc)
        
        # Insert into MongoDB
        if documents:
            result = await users_collection.insert_many(documents)
            print(f"Successfully migrated {len(result.inserted_ids)} users to MongoDB")
        
        # Create indexes
        await users_collection.create_index("email", unique=True)
        await users_collection.create_index("created_at")
        print("Created indexes for users collection")
        
    except Exception as e:
        print(f"Error during user migration: {e}")
    finally:
        conn.close()
        mongo_client.close()

async def main():
    """Main migration function"""
    print(f"Starting migration to MongoDB at {MONGODB_URL}")
    print(f"Database: {DATABASE_NAME}")
    
    await migrate_legal_acts()
    await migrate_users()
    
    print("Migration completed!")

if __name__ == "__main__":
    asyncio.run(main())
