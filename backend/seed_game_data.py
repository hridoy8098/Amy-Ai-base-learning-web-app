"""
Seed game system with sample curriculum data
Run: python seed_game_data.py
"""

from core.database import SessionLocal
from models.game_models import GameSubject, GameTopic, GameLevel, LevelLock
from datetime import datetime

db = SessionLocal()

# ═══════════════════════════════════════════════════════════════════════════
# SUBJECTS
# ═══════════════════════════════════════════════════════════════════════════

subjects_data = [
    {
        "name": "Grammar",
        "description": "Master English grammar fundamentals",
        "icon": "📝",
        "color": "#4CAF50",
        "topics": [
            {
                "name": "Parts of Speech",
                "description": "Nouns, Verbs, Adjectives, Adverbs",
                "levels": [
                    {"name": "Nouns 101", "difficulty": "easy", "xp_reward": 50},
                    {"name": "Verbs Basics", "difficulty": "easy", "xp_reward": 50},
                    {"name": "Adjectives", "difficulty": "medium", "xp_reward": 100},
                ]
            },
            {
                "name": "Tenses",
                "description": "Present, Past, Future tenses",
                "levels": [
                    {"name": "Present Tense", "difficulty": "easy", "xp_reward": 50},
                    {"name": "Past Tense", "difficulty": "medium", "xp_reward": 100},
                    {"name": "Future Tense", "difficulty": "medium", "xp_reward": 100},
                ]
            }
        ]
    },
    {
        "name": "Vocabulary",
        "description": "Build your word power",
        "icon": "📖",
        "color": "#2196F3",
        "topics": [
            {
                "name": "Basic Words",
                "description": "Essential 1000 words",
                "levels": [
                    {"name": "Colors & Numbers", "difficulty": "easy", "xp_reward": 50},
                    {"name": "Family & Friends", "difficulty": "easy", "xp_reward": 50},
                ]
            },
            {
                "name": "Advanced Words",
                "description": "Academic vocabulary",
                "levels": [
                    {"name": "Science Terms", "difficulty": "hard", "xp_reward": 200},
                    {"name": "Business English", "difficulty": "hard", "xp_reward": 200},
                ]
            }
        ]
    },
    {
        "name": "Pronunciation",
        "description": "Speak like a native",
        "icon": "🎤",
        "color": "#FF9800",
        "topics": [
            {
                "name": "Vowels",
                "description": "Vowel sounds practice",
                "levels": [
                    {"name": "Short Vowels", "difficulty": "easy", "xp_reward": 50},
                    {"name": "Long Vowels", "difficulty": "medium", "xp_reward": 100},
                ]
            }
        ]
    },
    {
        "name": "Conversation",
        "description": "Real-world speaking practice",
        "icon": "💬",
        "color": "#9C27B0",
        "topics": [
            {
                "name": "Greetings",
                "description": "Hello & Introductions",
                "levels": [
                    {"name": "Basic Greetings", "difficulty": "easy", "xp_reward": 50},
                    {"name": "Formal Introductions", "difficulty": "medium", "xp_reward": 100},
                ]
            }
        ]
    }
]

def seed_curriculum():
    """Create sample curriculum"""
    
    # Track order
    subject_order = 0
    
    for subject_data in subjects_data:
        # Create subject
        subject = GameSubject(
            name=subject_data["name"],
            description=subject_data["description"],
            icon=subject_data["icon"],
            color=subject_data["color"],
            order_index=subject_order,
            is_active=True,
            created_at=datetime.now()
        )
        db.add(subject)
        db.flush()
        subject_order += 1
        
        # Create topics
        topic_order = 0
        for topic_data in subject_data.get("topics", []):
            topic = GameTopic(
                subject_id=subject.id,
                name=topic_data["name"],
                description=topic_data["description"],
                order_index=topic_order,
                is_available=True,
                created_at=datetime.now()
            )
            db.add(topic)
            db.flush()
            topic_order += 1
            
            # Create levels
            level_order = 0
            prev_level = None
            for level_data in topic_data.get("levels", []):
                level = GameLevel(
                    topic_id=topic.id,
                    name=level_data["name"],
                    difficulty=level_data["difficulty"],
                    xp_reward=level_data["xp_reward"],
                    order_index=level_order,
                    is_available=level_order == 0,  # Only first level available
                    created_at=datetime.now()
                )
                db.add(level)
                db.flush()
                
                # Create level lock (except first level)
                if prev_level:
                    lock = LevelLock(
                        level_id=level.id,
                        prerequisite_level_id=prev_level.id,
                        mastery_required=80  # Need 80% mastery to unlock
                    )
                    db.add(lock)
                
                prev_level = level
                level_order += 1
    
    db.commit()
    print("✅ Curriculum data seeded successfully!")
    print(f"   Created {len(subjects_data)} subjects")
    print("   Run admin panel: /admin/game to view/manage")

if __name__ == "__main__":
    try:
        seed_curriculum()
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()
