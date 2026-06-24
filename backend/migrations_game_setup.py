"""
Database Migration Script - Game Learning System
Run this to create all game learning tables in MySQL

Usage:
    python migrations/create_game_tables.py
"""

from sqlalchemy import create_engine, text
from core.database import Base, DATABASE_URL
from models.game_models import *
import os
import sys

def create_tables():
    """Create all game learning tables"""
    try:
        engine = create_engine(DATABASE_URL, echo=True)
        
        print("=" * 80)
        print("🎮 Creating Game Learning System Tables...")
        print("=" * 80)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("\n✅ All tables created successfully!\n")
        
        # Print created tables
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES LIKE 'game_%'"))
            tables = result.fetchall()
            
            print("📋 Created Tables:")
            for table in tables:
                print(f"   ✓ {table[0]}")
        
        print("\n" + "=" * 80)
        print("✅ Migration Complete!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False


def drop_tables(confirm=True):
    """Drop all game learning tables (use with caution!)"""
    if confirm:
        response = input("\n⚠️  WARNING: This will DELETE all game learning tables! Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled.")
            return False
    
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        
        print("\n🗑️  Dropping Game Learning Tables...")
        Base.metadata.drop_all(bind=engine)
        
        print("✅ All game learning tables dropped!\n")
        return True
        
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return False


def seed_initial_data():
    """Seed initial game data (subjects, topics, etc.)"""
    from sqlalchemy.orm import sessionmaker
    from models.game_models import GameSubject, GameTopic
    from datetime import datetime
    
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("\n📚 Seeding Initial Data...")
        
        # Create subjects if not exist
        subjects_data = [
            {"name": "Grammar", "icon": "📖"},
            {"name": "Vocabulary", "icon": "📚"},
            {"name": "Speaking", "icon": "🎤"},
            {"name": "Reading", "icon": "👀"},
            {"name": "Writing", "icon": "✍️"},
        ]
        
        for subj in subjects_data:
            existing = db.query(GameSubject).filter_by(name=subj['name']).first()
            if not existing:
                new_subject = GameSubject(
                    name=subj['name'],
                    icon=subj['icon'],
                    description=f"Learn {subj['name'].lower()} in English"
                )
                db.add(new_subject)
        
        db.commit()
        print("✅ Initial data seeded!\n")
        return True
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def check_database():
    """Check database connection and existing tables"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!\n")
        
        # Check for existing game tables
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES LIKE 'game_%'"))
            tables = result.fetchall()
            
            if tables:
                print(f"📋 Found {len(tables)} existing game tables:")
                for table in tables:
                    print(f"   ✓ {table[0]}")
            else:
                print("⚠️  No game tables found (database is empty)\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🎮 Amy_Ai Game Learning System - Database Migration")
    print("=" * 80 + "\n")
    
    # Check connection first
    if not check_database():
        sys.exit(1)
    
    # Handle arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'create':
            create_tables()
        elif command == 'drop':
            drop_tables(confirm=True)
        elif command == 'seed':
            seed_initial_data()
        elif command == 'check':
            check_database()
        else:
            print("Unknown command!")
            print("\nUsage:")
            print("  python migrations/create_game_tables.py create    # Create tables")
            print("  python migrations/create_game_tables.py drop      # Drop tables")
            print("  python migrations/create_game_tables.py seed      # Seed initial data")
            print("  python migrations/create_game_tables.py check     # Check database")
    else:
        # Default: create tables
        create_tables()
        seed_initial_data()
