# Sudan News Pipeline

The producer/worker component of the Sudanese News Aggregator system. This service handles RSS feed aggregation, NLP analysis, and event clustering using machine learning models.

## Features

- **RSS Feed Aggregation**: Fetches articles from 25+ Sudanese and international news sources
- **NLP Analysis**: Extracts entities (people, cities, organizations) using Google GenAI
- **Event Clustering**: Groups related articles using semantic embeddings
- **Concurrent Safety**: File-based locking prevents overlapping pipeline runs
- **Configurable**: Environment-based configuration for all parameters
- **Containerized**: Docker support for easy deployment

## Architecture

```
RSS Feeds → Aggregation → NLP Analysis → Clustering → Database
```

## Installation

### Prerequisites
- Python 3.11+
- Access to shared_models package

### Setup

1. **Clone and navigate**:
   ```bash
   cd sudan-news-pipeline
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

4. **Initialize database** (if not already done):
   ```bash
   cd ../shared_models
   alembic upgrade head
   cd ../sudan-news-pipeline
   ```

## Usage

### Command Line Interface

The pipeline provides several CLI commands:

```bash
# Run full pipeline (aggregate + cluster)
python src/run_pipeline.py run-once

# Run only aggregation phase
python src/run_pipeline.py aggregate-only

# Run only clustering phase
python src/run_pipeline.py cluster-only

# Backfill news from last N days
python src/run_pipeline.py backfill --days 7
```

### Scheduled Execution

For development/testing, use the scheduler:

```bash
python tasks/scheduler.py
```

For production, set up a cron job:

```bash
# Add to crontab (crontab -e)
0 */6 * * * cd /path/to/sudan-news-pipeline && python src/run_pipeline.py run-once >> pipeline.log 2>&1
```

## Configuration

All settings are configurable via environment variables in `.env`:

### Database
- `DATABASE_URL`: Database connection string

### API Keys
- `GOOGLE_API_KEY`: Google GenAI API key for NLP
- `HF_TOKEN`: HuggingFace token for model access

### Model Settings
- `EMBEDDING_MODEL`: Sentence transformer model (default: google/embeddinggemma-300m)
- `NLP_MODEL`: Google GenAI model (default: gemma-3-27b-it)

### Clustering Parameters
- `SIMILARITY_THRESHOLD`: Similarity threshold for clustering (default: 0.5)
- `TIME_WINDOW_HOURS`: Time window for clustering (default: 72)
- `MAX_ARTICLES_PER_CLUSTER`: Maximum articles per cluster (default: 50)

### Pipeline Settings
- `BATCH_SIZE`: Processing batch size (default: 10)
- `MAX_RETRIES`: API retry attempts (default: 3)
- `REQUEST_TIMEOUT`: HTTP request timeout (default: 15)

## Docker Deployment

### Build Image
```bash
docker build -t sudan-news-pipeline .
```

### Run Container
```bash
docker run --env-file .env -v $(pwd)/data:/app/data sudan-news-pipeline
```

### Docker Compose Example
```yaml
version: '3.8'
services:
  pipeline:
    build: .
    env_file: .env
    volumes:
      - ./data:/app/data
    command: ["python", "src/run_pipeline.py", "run-once"]
```

## RSS Feed Sources

The pipeline aggregates from 25+ sources including:
- Local Sudanese news: Sudanile, Dabanga, Radio Tamazuj
- International coverage: CNN Arabic, Al Jazeera, France 24
- Regional news: Alalam, RT Arabic, Sky News Arabia

## Concurrency Control

The pipeline uses file-based locking (`pipeline.lock`) to prevent concurrent runs that could:
- Duplicate article processing
- Interfere with clustering operations
- Cause database conflicts

## Logging

Logs are written to both console and file (`pipeline.log`):
- INFO: Normal operations
- WARNING: Recoverable issues
- ERROR: Failures requiring attention

## Monitoring

Monitor pipeline health by checking:
- Log files for errors
- Database for new articles/clusters
- Lock file presence (indicates running pipeline)

## Troubleshooting

### Common Issues

**Pipeline lock errors**: Remove `pipeline.lock` if pipeline crashed

**API quota exceeded**: Check Google GenAI quotas and billing

**Database connection failed**: Verify DATABASE_URL and permissions

**Memory issues**: Reduce BATCH_SIZE for lower memory usage

**Model download failed**: Check HF_TOKEN and internet connection

### Debug Mode
Set `LOG_LEVEL=DEBUG` for detailed logging.

## Performance Tuning

- **CPU Optimization**: Adjust BATCH_SIZE based on available RAM
- **API Limits**: Configure REQUEST_TIMEOUT and MAX_RETRIES
- **Clustering**: Tune SIMILARITY_THRESHOLD for accuracy vs speed
- **Database**: Use PostgreSQL for production workloads

## Security

- Store API keys in environment variables only
- Use non-root user in Docker containers
- Implement proper logging (avoid logging sensitive data)
- Regular dependency updates for security patches
