#!/usr/bin/env python3
"""
Script to populate content_hash for existing articles in the database.

This script should be run after the content_hash column has been added
to ensure all existing articles have their hashes computed for proper deduplication.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared_models.db import get_session
from shared_models.repositories.article_repository import ArticleRepository
from shared_models.models import Article
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_content_hashes():
    """Populate content_hash for all articles that don't have one."""
    logger.info("Starting content hash population for existing articles...")

    with get_session() as session:
        # Get all articles without content_hash
        articles_without_hash = session.query(Article).filter(Article.content_hash.is_(None)).all()

        if not articles_without_hash:
            logger.info("No articles found without content_hash. All articles already have hashes.")
            return

        logger.info(f"Found {len(articles_without_hash)} articles without content_hash")

        # Create repository instance for hash computation
        repo = ArticleRepository(session)

        # First pass: compute hashes and identify duplicates
        hash_to_articles = {}
        for article in articles_without_hash:
            content_hash = repo._compute_content_hash(article.headline, article.description)

            if content_hash not in hash_to_articles:
                hash_to_articles[content_hash] = []
            hash_to_articles[content_hash].append(article)

        # Second pass: assign hashes, keeping only the first article for each hash
        updated_count = 0
        duplicates_found = 0

        for content_hash, articles in hash_to_articles.items():
            if len(articles) > 1:
                # Multiple articles with same content - keep the first one (by ID)
                articles.sort(key=lambda a: a.id)  # Sort by ID to be deterministic
                primary_article = articles[0]
                duplicates = articles[1:]

                logger.warning(f"Found {len(articles)} duplicate articles with hash {content_hash[:16]}...")
                logger.warning(f"  Keeping article {primary_article.id}, marking others as duplicates")

                # Mark duplicates (you could delete them or flag them)
                for duplicate in duplicates:
                    # Option 1: Delete duplicates (uncomment if desired)
                    # session.delete(duplicate)

                    # Option 2: Mark as duplicate by setting a special hash (current approach)
                    duplicate.content_hash = f"DUPLICATE_OF_{primary_article.id}"
                    duplicates_found += 1

            # Set hash for the primary article
            articles[0].content_hash = content_hash
            updated_count += 1

            # Log progress every 50 articles
            if updated_count % 50 == 0:
                logger.info(f"Processed {updated_count} unique content hashes")

        # Commit all changes
        session.commit()
        logger.info(f"Successfully populated content_hash for {updated_count} articles")
        logger.info(f"Found and handled {duplicates_found} duplicate articles")

        # Check for any remaining articles without hashes
        remaining = session.query(Article).filter(Article.content_hash.is_(None)).count()
        if remaining > 0:
            logger.warning(f"Warning: {remaining} articles still don't have content_hash")
        else:
            logger.info("All articles now have content_hash populated")

if __name__ == "__main__":
    populate_content_hashes()
