# Sudanese News Aggregator - Technical Architecture Report

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Components](#architecture-components)
3. [Technology Stack](#technology-stack)
4. [Database Schema](#database-schema)
5. [Data Processing Pipeline](#data-processing-pipeline)
6. [API Design](#api-design)
7. [Special Features](#special-features)
8. [Deployment & Operations](#deployment--operations)
9. [Development Workflow](#development-workflow)
10. [Security Considerations](#security-considerations)

## System Overview

The Sudanese News Aggregator is a comprehensive news aggregation and analysis system designed to collect, process, and serve Sudanese news from multiple sources using AI-powered event detection and clustering.

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│ sudan-news-     │◄──►│ shared_models   │◄──►│ sudan-news-     │
│    pipeline     │    │                 │    │     api         │
│                 │    │ • SQLAlchemy    │    │                 │
│ • RSS Aggregation│    │ • Repositories │    │ • Flask API     │
│ • NLP Analysis   │    │ • Migrations   │    │ • Web Interface │
│ • Event Clustering│   │ • Utilities    │    │ • REST Endpoints│
│ • ML Processing  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Responsibilities

- **sudan-news-pipeline**: Producer service handling data ingestion, NLP processing, and event clustering
- **shared_models**: Common database layer with SQLAlchemy models and repository patterns
- **sudan-news-api**: Consumer service providing REST API and web interface for clients

## Architecture Components

### sudan-news-pipeline

**Location**: `sudan-news-pipeline/`

**Responsibilities**:
- RSS feed aggregation from 25+ Sudanese and international news sources
- Article filtering and deduplication using content hashing
- NLP entity extraction using Google GenAI
- Semantic clustering using sentence transformers
- Bias analysis and blindspot detection
- Trending topic identification

**Key Files**:
- `src/run_pipeline.py`: Main CLI interface with commands for aggregation, clustering, and backfill
- `src/aggregator.py`: RSS feed parsing and article extraction
- `src/nlp_pipeline.py`: Google GenAI integration for entity extraction
- `src/clustering.py`: Semantic similarity clustering using embeddings
- `config.py`: Configuration management for feeds, API keys, and parameters

**Processing Flow**:
```
RSS Feeds → Article Parsing → Sudan Relevance Filter → NLP Analysis → Entity Storage → Clustering → Database
```

### shared_models

**Location**: `shared_models/`

**Responsibilities**:
- Database schema definition and migrations
- Repository pattern implementation for data access
- Shared utilities and timezone handling
- Database connection management

**Key Files**:
- `models.py`: SQLAlchemy ORM models with custom JSON type for cross-database compatibility
- `repositories/`: Repository classes for each entity (Article, Cluster, Entity, etc.)
- `migrations/`: Alembic migration scripts for schema evolution
- `db.py`: Database session management and connection pooling

**Repository Pattern**:
```python
# Example usage
with get_session() as session:
    repo = ArticleRepository(session)
    articles = repo.get_recent_unclustered(hours=24)
```

### sudan-news-api

**Location**: `sudan-news-api/`

**Responsibilities**:
- REST API endpoints for mobile applications
- Responsive web interface with Arabic RTL support
- Push notification management via Firebase
- Caching and performance optimization

**Key Files**:
- `src/app.py`: Main Flask application with routes and API endpoints
- `src/notification_service.py`: Firebase integration for push notifications
- `templates/`: Jinja2 templates for web interface
- `static/`: CSS, JS, and image assets

**API Structure**:
- `/api/clusters`: Paginated cluster listings
- `/api/cluster/<id>`: Detailed cluster information
- `/api/articles`: Filtered article search
- `/api/register_token`: Push notification registration

## Technology Stack

### Core Framework
- **Python 3.11+**: Primary programming language
- **Flask 2.0+**: Web framework for API and web interface
- **SQLAlchemy 1.4+**: ORM for database operations
- **Alembic 1.7+**: Database migration management

### Machine Learning & AI
- **Google Generative AI**: NLP entity extraction and categorization
- **Sentence Transformers**: Text embedding generation for clustering
- **PyTorch 2.0+**: Deep learning framework
- **Transformers**: HuggingFace model integration

### Data Processing
- **Feedparser**: RSS/Atom feed parsing
- **BeautifulSoup4**: HTML content extraction
- **Requests**: HTTP client for API calls
- **Python-DateUtil**: Date/time parsing and manipulation

### Infrastructure & Deployment
- **Docker**: Containerization for all components
- **Gunicorn**: WSGI server for production deployment
- **Firebase Admin**: Push notification service
- **Flask-CORS**: Cross-origin resource sharing

### Development & Testing
- **pytest**: Unit and integration testing
- **Black**: Code formatting
- **Flake8**: Linting and style checking
- **MyPy**: Static type checking

## Database Schema

### Entity-Relationship Diagram

```
Sources ──── Articles ──── Entities
    │           │
    │           │
    └───────────┼────────── Clusters ──── UserTokens
                │               │
                Users           │
                                │
                                └─────────── Users
```

### Core Tables

#### Sources
```sql
CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR,
    url VARCHAR,
    language VARCHAR,
    owner VARCHAR,
    founded_at VARCHAR,
    hq_location VARCHAR,
    bias VARCHAR
);
```

**Purpose**: Stores information about news sources (RSS feeds)

#### Articles
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER REFERENCES sources(id),
    headline TEXT,
    description TEXT,
    published_at VARCHAR,
    article_url VARCHAR,
    image_url VARCHAR,
    created_at VARCHAR,
    updated_at VARCHAR,
    category VARCHAR,  -- 'local' or 'international'
    content_hash VARCHAR UNIQUE  -- For deduplication
);
```

**Purpose**: Individual news articles with metadata

#### Clusters
```sql
CREATE TABLE clusters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    number_of_sources INTEGER,
    published_at VARCHAR,
    created_at VARCHAR,

    -- Blindspot detection
    blindspot_type VARCHAR,
    bias_coverage_pro INTEGER DEFAULT 0,
    bias_coverage_neutral INTEGER DEFAULT 0,
    bias_coverage_oppose INTEGER DEFAULT 0,
    bias_balance_score FLOAT DEFAULT 0.0,

    -- Trending features
    coverage_velocity FLOAT DEFAULT 0.0,
    is_trending BOOLEAN DEFAULT 0,
    first_seen_at VARCHAR,
    last_coverage_check VARCHAR,
    coverage_history TEXT  -- JSON stored as TEXT
);
```

**Purpose**: Groups of related articles representing news events

#### Entities
```sql
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER REFERENCES articles(id),
    people TEXT,  -- JSON array
    cities TEXT,  -- JSON array
    regions TEXT, -- JSON array
    countries TEXT, -- JSON array
    organizations TEXT, -- JSON array
    political_parties_and_militias TEXT, -- JSON array
    brands TEXT, -- JSON array
    job_titles TEXT, -- JSON array
    category VARCHAR,  -- NLP category like 'سياسة'
    created_at VARCHAR
);
```

**Purpose**: NLP-extracted entities from article content

#### Association Tables

**cluster_articles**: Many-to-many relationship between clusters and articles
```sql
CREATE TABLE cluster_articles (
    cluster_id INTEGER REFERENCES clusters(id),
    article_id INTEGER REFERENCES articles(id),
    similarity_score FLOAT,
    PRIMARY KEY (cluster_id, article_id)
);
```

**Users & UserTokens**: For push notification management

### Schema Evolution

The database schema has evolved through several migrations:

1. **Initial Schema** (`90fd508fad86`): Basic tables for sources, articles, clusters, entities
2. **Source Details** (`8fa321b4b617`): Added metadata fields to sources table
3. **Content Hash** (`0a220c51a87d`): Added deduplication via content hashing
4. **Blindspot & Trending** (`fcef1900e02b`): Advanced features for bias analysis and trending detection

## Data Processing Pipeline

### Phase 1: RSS Aggregation

1. **Feed Discovery**: System maintains list of 25+ RSS feeds from Sudanese and international sources
2. **Article Extraction**: Parse RSS feeds using feedparser library
3. **Content Filtering**: Apply Sudan-relevance filter for international sources
4. **Deduplication**: Check content hash against existing articles
5. **Storage**: Insert new articles into database

### Phase 2: NLP Analysis

1. **Text Preparation**: Combine headline + description for analysis
2. **Entity Extraction**: Use Google GenAI to identify:
   - People, cities, regions, countries
   - Organizations, political parties
   - Brands, job titles
3. **Categorization**: Classify articles by topic (politics, security, economy, etc.)
4. **Storage**: Save entities as JSON in entities table

### Phase 3: Event Clustering

1. **Article Selection**: Get unclustered articles from last 24 hours
2. **Embedding Generation**: Create semantic embeddings using sentence transformers
3. **Similarity Calculation**: Compute pairwise similarity scores
4. **Clustering**: Group articles using similarity threshold (default: 0.5)
5. **Cluster Creation**: Store clusters with metadata and article relationships

### Phase 4: Feature Enhancement

1. **Bias Analysis**: Calculate coverage distribution across different bias perspectives
2. **Blindspot Detection**: Identify events with imbalanced coverage
3. **Trending Detection**: Monitor coverage velocity and identify rising topics

## API Design

### REST Endpoints

#### Cluster Endpoints
- `GET /api/clusters`: Paginated list of clusters with filtering
  - Query params: `page`, `limit`, `q` (search), `category`, `city`, `has_entities`
  - Response: Mobile-optimized cluster summaries

- `GET /api/cluster/{id}`: Detailed cluster information
  - Response: Complete cluster data with all articles and entities

#### Content Endpoints
- `GET /api/articles`: Articles with filtering options
- `GET /api/categories`: Available news categories
- `GET /api/cities`: Unique cities from entities

#### Notification Endpoints
- `POST /api/register_token`: Register device for push notifications
- `POST /api/send_notification`: Send custom notifications
- `POST /api/notify_new_cluster/{id}`: Notify about new clusters
- `POST /api/notify_popular_clusters`: Notify about popular clusters

### Response Formats

#### Mobile API Response (Clusters)
```json
{
  "id": 123,
  "headline": "Event title",
  "description": "First article description",
  "image_url": "https://...",
  "country_city": "Sudan/Khartoum",
  "first_date_of_publication": "2025-01-15T10:30:00",
  "number_of_sources": 5,
  "bias_distribution": {
    "pro": 2,
    "neutral": 1,
    "oppose": 2
  },
  "is_trending": true
}
```

#### Web Interface Features
- **Responsive Design**: Mobile-first approach with Arabic RTL support
- **Real-time Search**: Dynamic filtering and pagination
- **Infinite Scroll**: Efficient loading of large datasets
- **Template Filters**: Arabic date/time formatting

### Caching Strategy
- **Cluster Listings**: 5-minute cache (`max-age=300`)
- **Cluster Details**: 10-minute cache (`max-age=600`)
- **Categories/Cities**: 1-hour cache (`max-age=3600`)
- **ETags**: Automatic ETag generation for conditional requests

## Special Features

### Bias Analysis & Blindspot Detection

**Purpose**: Identify news events with imbalanced coverage across different political perspectives

**Implementation**:
- Track source bias ratings (Pro-SAF, Neutral, Oppose-SAF)
- Calculate coverage distribution for each cluster
- Flag clusters with insufficient diverse coverage as "blindspots"

**Database Fields**:
- `bias_coverage_pro/neutral/oppose`: Count of sources by bias
- `bias_balance_score`: Calculated balance metric
- `blindspot_type`: Classification of coverage gap

### Trending Topic Detection

**Purpose**: Identify rapidly emerging news topics

**Implementation**:
- Monitor coverage velocity (articles per hour)
- Track coverage history over time
- Apply trending algorithm based on growth rate

**Database Fields**:
- `coverage_velocity`: Current growth rate
- `is_trending`: Boolean flag
- `first_seen_at`: Initial detection timestamp
- `coverage_history`: Time-series data as JSON

### Arabic Language Support

**Features**:
- RTL (Right-to-Left) text rendering
- Arabic date/time formatting filters
- Localized category names
- UTF-8 encoding throughout

**Implementation**:
- Jinja2 template filters for Arabic formatting
- CSS direction: rtl for Arabic content
- Unicode support in database (SQLite/PostgreSQL)

### Push Notification System

**Architecture**:
- Firebase Cloud Messaging integration
- Device token management
- Automated notifications for new/popular clusters

**Features**:
- Cross-platform (Android/iOS) support
- Custom notification payloads
- Bulk notification sending
- Token lifecycle management

## Deployment & Operations

### Docker Containerization

**Pipeline Container**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/run_pipeline.py", "run-once"]
```

**API Container**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "--config", "gunicorn.conf.py", "src.app:app"]
```

### Production Deployment

**Gunicorn Configuration**:
```python
# gunicorn.conf.py
workers = 4
bind = "0.0.0.0:8000"
timeout = 30
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
```

**Nginx Reverse Proxy**:
```nginx
server {
    listen 80;
    server_name news.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Scheduling

**Cron Job for Pipeline**:
```bash
# crontab -e
0 */6 * * * cd /path/to/sudan-news-pipeline && python src/run_pipeline.py run-once >> pipeline.log 2>&1
```

### Monitoring

**Health Checks**:
- `/health` endpoint for API availability
- Database connection monitoring
- Pipeline execution status via log files

**Key Metrics**:
- API response times
- Pipeline execution duration
- Database query performance
- Error rates and logging

## Development Workflow

### Local Development Setup

1. **Environment Setup**:
   ```bash
   # Clone repository
   git clone <repository-url>
   cd sudanese-news-aggregator

   # Setup shared models
   cd shared_models
   pip install -e .
   python db_create.py

   # Setup pipeline
   cd ../sudan-news-pipeline
   pip install -r requirements.txt
   cp .env.example .env

   # Setup API
   cd ../sudan-news-api
   pip install -r requirements.txt
   cp .env.example .env
   ```

2. **Database Initialization**:
   ```bash
   cd shared_models
   alembic upgrade head
   ```

3. **Run Components**:
   ```bash
   # Terminal 1: Start API
   cd sudan-news-api && python src/app.py

   # Terminal 2: Run pipeline
   cd sudan-news-pipeline && python src/run_pipeline.py run-once
   ```

### Testing Strategy

**Unit Tests**:
- Repository classes in `shared_models/tests/`
- Individual component testing

**Integration Tests**:
- End-to-end pipeline testing
- API endpoint testing

**Code Quality**:
- Black for formatting
- Flake8 for linting
- MyPy for type checking

### Database Migrations

**Creating New Migrations**:
```bash
cd shared_models
alembic revision --autogenerate -m "Add new feature"
alembic upgrade head
```

## Security Considerations

### API Security
- Input validation on all endpoints
- SQL injection prevention via SQLAlchemy ORM
- CORS configuration for authorized origins

### Data Protection
- No sensitive data logging
- Environment variable configuration
- Secure API key management

### Infrastructure Security
- Non-root Docker containers
- Minimal attack surface
- Regular dependency updates

### Authentication
- Token-based device registration
- Firebase authentication for notifications
- No user authentication (public API)

---

**Built with Python, Flask, SQLAlchemy, and AI for comprehensive Sudanese news aggregation and analysis.**

*Report generated on: December 1, 2025*
*Codebase version: Latest commit on main branch*
