# Shared Models Package

This package contains the shared SQLAlchemy models, repositories, and database utilities for the Sudanese News Aggregator system.

## Structure

- `models.py`: SQLAlchemy ORM models for all database tables
- `db.py`: Database connection and session management
- `repositories/`: Repository classes for database operations
- `migrations/`: Alembic migration scripts

## Installation

For development with editable installs:
```bash
pip install -e .
```

## Database Setup

Choose one of the following approaches:

### Option 1: Alembic Migrations (Recommended for Production)

1. Set your database URL in environment variables:
   ```bash
   export DATABASE_URL="sqlite:///news_aggregator.db"  # or PostgreSQL URL
   ```

2. Run migrations:
   ```bash
   alembic upgrade head
   ```

3. For schema changes:
   ```bash
   # Generate new migration
   alembic revision --autogenerate -m "Description of changes"

   # Apply migration
   alembic upgrade head
   ```

### Option 2: Quick Setup (SQLite Development Only)

For quick development setup with SQLite:
```bash
python db_create.py
```

This creates all tables and optionally populates sample data.

## Usage

```python
from shared_models.db import get_session
from shared_models.repositories.article_repository import ArticleRepository

with get_session() as session:
    repo = ArticleRepository(session)
    articles = repo.get_recent_unclustered(hours=24)
```

## Models

- `Source`: News sources (RSS feeds)
- `Article`: Individual news articles
- `Cluster`: Event clusters grouping related articles
- `Entity`: NLP-extracted entities from articles
- `User`: User accounts (for future use)
- `UserToken`: Push notification tokens

## Repositories

- `ArticleRepository`: Article CRUD and filtering
- `ClusterRepository`: Cluster management and similarity matching
- `EntityRepository`: Entity extraction results
- `SourceRepository`: Source management
- `TokenRepository`: Push notification token management

## JSON Fields

Entity fields (people, cities, etc.) are stored as JSON. The custom `JSONType` handles serialization/deserialization and works with both SQLite and PostgreSQL.
