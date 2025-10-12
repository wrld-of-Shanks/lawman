#!/usr/bin/env python3
"""
Test MongoDB connection script
"""
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    """Test MongoDB connection"""
    mongodb_url = os.getenv("MONGODB_URL")
    database_name = os.getenv("DATABASE_NAME", "specter_legal")
    
    if not mongodb_url:
        print("❌ MONGODB_URL environment variable not set")
        print("Set it like: export MONGODB_URL='mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority'")
        return False
    
    print(f"🔗 Testing connection to: {mongodb_url}")
    print(f"📊 Database: {database_name}")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test database access
        collections = await db.list_collection_names()
        print(f"📁 Collections in database: {collections}")
        
        # Test users collection
        users_collection = db.users
        user_count = await users_collection.count_documents({})
        print(f"👥 Users in database: {user_count}")
        
        # Test legal_acts collection
        legal_acts_collection = db.legal_acts
        acts_count = await legal_acts_collection.count_documents({})
        print(f"⚖️ Legal acts in database: {acts_count}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if success:
        print("\n🎉 MongoDB is ready for deployment!")
    else:
        print("\n💡 Please check your MongoDB configuration and try again.")
