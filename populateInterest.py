"""
Populate Database with Interests
Run this script to add default interests to your database
"""

from app.core.database import SessionLocal, engine, Base
from app.models.interest import Interest

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def populate_interests():
    """Add default interests to the database"""
    
    db = SessionLocal()
    
    # Check if interests already exist
    existing = db.query(Interest).count()
    if existing > 0:
        print(f"✅ Database already has {existing} interests!")
        print("No need to populate.")
        db.close()
        return
    
    # Define interests by category
    interests_data = [
        # Sports & Fitness
        {"category": "sports", "name": "Football", "icon": "⚽"},
        {"category": "sports", "name": "Basketball", "icon": "🏀"},
        {"category": "sports", "name": "Tennis", "icon": "🎾"},
        {"category": "sports", "name": "Swimming", "icon": "🏊"},
        {"category": "sports", "name": "Yoga", "icon": "🧘"},
        {"category": "sports", "name": "Gym", "icon": "💪"},
        {"category": "sports", "name": "Running", "icon": "🏃"},
        {"category": "sports", "name": "Cycling", "icon": "🚴"},
        {"category": "sports", "name": "Hiking", "icon": "🥾"},
        {"category": "sports", "name": "Cricket", "icon": "🏏"},
        
        # Arts & Culture
        {"category": "arts", "name": "Painting", "icon": "🎨"},
        {"category": "arts", "name": "Photography", "icon": "📷"},
        {"category": "arts", "name": "Music", "icon": "🎵"},
        {"category": "arts", "name": "Dance", "icon": "💃"},
        {"category": "arts", "name": "Theatre", "icon": "🎭"},
        {"category": "arts", "name": "Reading", "icon": "📚"},
        {"category": "arts", "name": "Writing", "icon": "✍️"},
        {"category": "arts", "name": "Poetry", "icon": "📝"},
        
        # Entertainment
        {"category": "entertainment", "name": "Movies", "icon": "🎬"},
        {"category": "entertainment", "name": "Gaming", "icon": "🎮"},
        {"category": "entertainment", "name": "Anime", "icon": "🎌"},
        {"category": "entertainment", "name": "TV Shows", "icon": "📺"},
        {"category": "entertainment", "name": "Concerts", "icon": "🎤"},
        {"category": "entertainment", "name": "Stand-up Comedy", "icon": "😂"},
        
        # Food & Drink
        {"category": "food", "name": "Cooking", "icon": "👨‍🍳"},
        {"category": "food", "name": "Baking", "icon": "🧁"},
        {"category": "food", "name": "Coffee", "icon": "☕"},
        {"category": "food", "name": "Wine Tasting", "icon": "🍷"},
        {"category": "food", "name": "Street Food", "icon": "🌮"},
        {"category": "food", "name": "Fine Dining", "icon": "🍽️"},
        
        # Technology
        {"category": "technology", "name": "Coding", "icon": "💻"},
        {"category": "technology", "name": "AI/ML", "icon": "🤖"},
        {"category": "technology", "name": "Gadgets", "icon": "📱"},
        {"category": "technology", "name": "Blockchain", "icon": "⛓️"},
        {"category": "technology", "name": "Web Development", "icon": "🌐"},
        
        # Outdoor & Nature
        {"category": "outdoor", "name": "Camping", "icon": "⛺"},
        {"category": "outdoor", "name": "Trekking", "icon": "🏔️"},
        {"category": "outdoor", "name": "Gardening", "icon": "🌱"},
        {"category": "outdoor", "name": "Bird Watching", "icon": "🦅"},
        {"category": "outdoor", "name": "Beach", "icon": "🏖️"},
        
        # Learning & Development
        {"category": "learning", "name": "Languages", "icon": "🗣️"},
        {"category": "learning", "name": "History", "icon": "📜"},
        {"category": "learning", "name": "Science", "icon": "🔬"},
        {"category": "learning", "name": "Philosophy", "icon": "💭"},
        {"category": "learning", "name": "Meditation", "icon": "🧘‍♀️"},
        
        # Social & Community
        {"category": "social", "name": "Volunteering", "icon": "🤝"},
        {"category": "social", "name": "Networking", "icon": "👥"},
        {"category": "social", "name": "Travel", "icon": "✈️"},
        {"category": "social", "name": "Pet Care", "icon": "🐕"},
        {"category": "social", "name": "Fashion", "icon": "👗"},
    ]
    
    print("📝 Adding interests to database...")
    
    try:
        for interest_data in interests_data:
            interest = Interest(**interest_data)
            db.add(interest)
        
        db.commit()
        print(f"✅ Successfully added {len(interests_data)} interests!")
        print("\nInterests by category:")
        
        # Display added interests
        categories = {}
        for interest_data in interests_data:
            cat = interest_data['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(f"{interest_data['icon']} {interest_data['name']}")
        
        for category, items in categories.items():
            print(f"\n{category.upper()}:")
            for item in items:
                print(f"  - {item}")
                
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding interests: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  MeetZy - Populate Database with Interests")
    print("=" * 60)
    print()
    populate_interests()
    print()
    print("=" * 60)
    print("  Done! You can now use the interests in your app")
    print("=" * 60)