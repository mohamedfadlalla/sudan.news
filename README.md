# Sudanese News Aggregator

A comprehensive system for aggregating, clustering, and serving Sudanese news from multiple sources using AI-powered event detection.

## Architecture Overview

This project has been split into three main components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│ sudan-news-     │    │ shared_models   │    │ sudan-news-     │
│    pipeline     │◄──►│                 │◄──►│     api         │
│                 │    │                 │    │                 │
│ • RSS Aggregation│    │ • SQLAlchemy   │    │ • Flask API     │
│ • NLP Analysis   │    │ • Repositories │    │ • Web Interface │
│ • Event Clustering│   │ • Migrations   │    │ • REST Endpoints│
│ • ML Processing  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Components

- **`sudan-news-pipeline`**: Producer/worker service handling data ingestion and ML processing
- **`sudan-news-api`**: Consumer/web API serving clustered news to clients
- **`shared_models`**: Common database models, repositories, and utilities

## Quick Start

### Prerequisites

- Python 3.11+
- SQLite (default) or PostgreSQL
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd sudanese-news-aggregator
   ```

2. **Setup shared models**:
   ```bash
   cd shared_models
   pip install -e .
   python db_create.py  # Quick SQLite setup
   cd ..
   ```

3. **Setup pipeline**:
   ```bash
   cd sudan-news-pipeline
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   cd ..
   ```

4. **Setup API**:
   ```bash
   cd sudan-news-api
   pip install -r requirements.txt
   cp .env.example .env
   cd ..
   ```

### Running the System

1. **Run the pipeline** (fetch and process news):
   ```bash
   cd sudan-news-pipeline
   python src/run_pipeline.py run-once
   ```

2. **Start the API server**:
   ```bash
   cd sudan-news-api
   python src/app.py
   ```

3. **Access the web interface**:
   - Open http://localhost:5000 in your browser
   - API endpoints available at http://localhost:5000/api/

## Development Workflow

### Daily Development

1. **Activate virtual environment** (if using one)
2. **Run tests**:
   ```bash
   # Test shared models
   cd shared_models && python -m pytest tests/

   # Test pipeline components
   cd ../sudan-news-pipeline && python -m pytest  # (if tests added)

   # Test API
   cd ../sudan-news-api && python -m pytest  # (if tests added)
   ```

3. **Run the full system**:
   ```bash
   # Terminal 1: Start API
   cd sudan-news-api && python src/app.py

   # Terminal 2: Run pipeline
   cd sudan-news-pipeline && python src/run_pipeline.py run-once
   ```

### Adding New Features

1. **Database changes**: Modify `shared_models/models.py`, then create migration:
   ```bash
   cd shared_models
   alembic revision --autogenerate -m "Add new feature"
   alembic upgrade head
   ```

2. **Pipeline features**: Add to `sudan-news-pipeline/src/`
3. **API features**: Add to `sudan-news-api/src/`

### Testing

```bash
# Run all component tests
cd shared_models && python -m pytest tests/
cd ../sudan-news-pipeline && python -m pytest  # (future)
cd ../sudan-news-api && python -m pytest  # (future)
```

## Configuration

### Environment Variables

Create `.env` files in each component directory:

#### Pipeline (.env)
```bash
DATABASE_URL=sqlite:///news_aggregator.db
GOOGLE_API_KEY=your_google_genai_key
HF_TOKEN=your_huggingface_token
EMBEDDING_MODEL=google/embeddinggemma-300m
SIMILARITY_THRESHOLD=0.5
LOG_LEVEL=INFO
```

#### API (.env)
```bash
DATABASE_URL=sqlite:///news_aggregator.db
FLASK_ENV=development
SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
```

### Database Options

- **SQLite** (default): Simple file-based database, good for development
- **PostgreSQL**: Production-ready with better performance and JSON support

To use PostgreSQL:
```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/news_db"
cd shared_models && alembic upgrade head
```

## API Documentation

### Endpoints

- `GET /` - Web interface
- `GET /event/<id>` - Event details page
- `GET /api/clusters` - Paginated event clusters
- `GET /api/cluster/<id>` - Detailed cluster information
- `GET /api/categories` - Available categories
- `GET /api/articles` - Articles with filtering
- `POST /api/register_token` - Register push notification token
- `GET /health` - Health check

### Response Formats

See `sudan-news-api/README.md` for detailed API documentation.

## Deployment

### Docker Deployment

1. **Build images**:
   ```bash
   # Build pipeline
   cd sudan-news-pipeline && docker build -t sudan-news-pipeline .

   # Build API
   cd sudan-news-api && docker build -t sudan-news-api .
   ```

2. **Run with Docker Compose**:
   ```yaml
   # docker-compose.yml
   version: '3.8'
   services:
     db:
       image: postgres:13
       environment:
         POSTGRES_DB: news_db
         POSTGRES_USER: news_user
         POSTGRES_PASSWORD: news_pass

     pipeline:
       image: sudan-news-pipeline
       environment:
         - DATABASE_URL=postgresql://news_user:news_pass@db:5432/news_db
       depends_on:
         - db

     api:
       image: sudan-news-api
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://news_user:news_pass@db:5432/news_db
       depends_on:
         - db
   ```

### Production Server

1. **Setup Gunicorn**:
   ```bash
   cd sudan-news-api
   gunicorn --config gunicorn.conf.py src.app:app
   ```

2. **Setup Nginx** (reverse proxy):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Setup SSL** with Let's Encrypt

## Monitoring

### Health Checks

- API health: `GET /health`
- Database connectivity
- Pipeline execution status

### Logs

- Pipeline logs: `sudan-news-pipeline/pipeline.log`
- API logs: `sudan-news-api/access.log`, `error.log`
- Gunicorn logs (production)

### Metrics

Monitor:
- API response times
- Pipeline execution duration
- Database query performance
- Error rates

## Troubleshooting

### Common Issues

**Database connection failed**
- Check `DATABASE_URL` in `.env`
- Ensure database server is running
- Run migrations: `cd shared_models && alembic upgrade head`

**Pipeline not processing articles**
- Check API keys in pipeline `.env`
- Verify RSS feeds are accessible
- Check pipeline logs for errors

**API returning errors**
- Verify database has data
- Check API logs
- Test with `curl http://localhost:5000/health`

**Import errors**
- Ensure all components installed with `pip install -e`
- Check Python path includes project directories

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
```

Run with verbose output:
```bash
cd sudan-news-api && python src/app.py  # Shows Flask debug logs
cd sudan-news-pipeline && python src/run_pipeline.py run-once --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes with tests
4. Run full test suite
5. Submit pull request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests for new features

## License

This project is open source. See LICENSE file for details.

## Support

- **Issues**: GitHub Issues
- **Documentation**: Component README files
- **API Docs**: `sudan-news-api/README.md`

---

**Built with Flask, SQLAlchemy, and AI for Sudanese news aggregation and analysis.**
