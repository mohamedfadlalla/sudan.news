#!/usr/bin/env python3
"""
Database Creation Script for Sudanese News Aggregator

This script provides a quick way to create and populate the database
for development and testing purposes. It uses SQLAlchemy's create_all()
instead of Alembic migrations for simplicity.

Usage:
    python db_create.py

This is suitable for:
- Quick development setup
- SQLite databases
- Testing environments
- Initial project setup

For production deployments with schema versioning, use Alembic migrations instead.
"""

import os
import sys
import platform
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
if platform.system() == 'Windows':
    load_dotenv()
else:
    # On Ubuntu, load from absolute path
    load_dotenv('/var/www/sudanese_news/shared/.env')

# Setup path for imports
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from models import Base
from db import engine, get_session
from repositories.source_repository import SourceRepository
from repositories.article_repository import ArticleRepository
from repositories.entity_repository import EntityRepository

def create_database():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")

def populate_sample_data():
    """Populate database with sample data for development"""
    print("Populating sample data...")

    # Create session
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        # Initialize repositories
        source_repo = SourceRepository(session)
        article_repo = ArticleRepository(session)
        entity_repo = EntityRepository(session)

        # Create sample sources
        sources_data = [
            {"url": "https://sudanile.com/", "name": "Sudanile"},
            {"url": "https://www.dabangasudan.org/", "name": "Dabanga Sudan"},
            {"url": "https://www.aljazeera.net/", "name": "Al Jazeera"},
        ]

        sources = []
        for source_data in sources_data:
            source = source_repo.get_or_create_source(
                source_data["url"],
                source_data["name"]
            )
            sources.append(source)

        # Create sample articles
        articles_data = [
            {
                "source": sources[0],
                "headline": "Sample News Article 1",
                "description": "This is a sample news article for testing purposes.",
                "published_at": "2025-01-15T10:00:00",
                "article_url": "https://sudanile.com/sample1",
                "category": "local"
            },
            {
                "source": sources[1],
                "headline": "Sample News Article 2",
                "description": "Another sample article with different content.",
                "published_at": "2025-01-15T11:00:00",
                "article_url": "https://dabanga.org/sample2",
                "category": "local"
            },
            {
                "source": sources[2],
                "headline": "International News Sample",
                "description": "Sample international news article.",
                "published_at": "2025-01-15T12:00:00",
                "article_url": "https://aljazeera.net/sample3",
                "category": "international"
            }
        ]

        for article_data in articles_data:
            article = article_repo.insert_article(
                source_id=article_data["source"].id,
                headline=article_data["headline"],
                description=article_data["description"],
                published_at=article_data["published_at"],
                article_url=article_data["article_url"],
                category=article_data["category"]
            )

            # Add sample entities
            entity_repo.insert_entities(
                article_id=article.id,
                people=["Sample Person"],
                cities=["Khartoum"],
                countries=["Sudan"],
                organizations=["Sample Organization"],
                category="سياسة"
            )

        session.commit()
        print("✓ Sample data populated successfully")

    except Exception as e:
        session.rollback()
        print(f"✗ Error populating sample data: {e}")
        raise
    finally:
        session.close()

def main():
    """Main function"""
    print("Sudanese News Aggregator - Database Creation Script")
    print("=" * 50)

    # Check database URL
    from db import get_database_url
    db_url = get_database_url()
    print(f"Database URL: {db_url}")

    if "sqlite" not in db_url.lower():
        print("⚠️  Warning: This script is designed for SQLite databases.")
        print("   For PostgreSQL or other databases, use Alembic migrations instead.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return

    # Create database
    create_database()

    # Ask about sample data
    response = input("\nPopulate with sample data? (y/N): ")
    if response.lower() == 'y':
        populate_sample_data()

    print("\n✓ Database setup complete!")
    print("\nNext steps:")
    print("1. Run the pipeline: cd ../sudan-news-pipeline && python src/run_pipeline.py run-once")
    print("2. Start the API: cd ../sudan-news-api && python src/app.py")
    print("3. Visit http://localhost:5000")

if __name__ == "__main__":
    main()
