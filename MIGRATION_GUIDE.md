# Migration Guide: Sudanese News Aggregator Refactoring

This guide provides step-by-step instructions for migrating from the monolithic Flask application to the new microservices architecture.

## Overview

The refactoring maintains **100% backwards compatibility**, so existing deployments can continue operating during and after migration. The new architecture introduces three independent services that can be deployed gradually.

## Migration Strategies

### Strategy 1: Gradual Migration (Recommended)

Deploy new services alongside the existing system and migrate traffic incrementally.

#### Phase 1: Infrastructure Setup
```bash
# 1. Setup shared database layer
cd shared_models
pip install -e .
alembic upgrade head  # Migrate existing database

# 2. Deploy new API service (read-only)
cd ../sudan-news-api
docker build -t sudan-news-api .
docker run -d -p 8000:8000 --env-file .env sudan-news-api

# 3. Test API compatibility
curl "http://localhost:8000/api/clusters?page=1&limit=10"
```

#### Phase 2: Traffic Migration
```bash
# 1. Route read traffic to new API
# Update load balancer/reverse proxy to route:
# - /api/* → sudan-news-api:8000
# - /* (web) → sudan-news-api:8000

# 2. Monitor API responses and performance
# Compare responses between old and new APIs

# 3. Gradually increase traffic to new API
```

#### Phase 3: Pipeline Migration
```bash
# 1. Deploy pipeline service
cd sudan-news-pipeline
docker build -t sudan-news-pipeline .
docker run -d --env-file .env sudan-news-pipeline

# 2. Run parallel processing
# Both old and new pipelines can run simultaneously

# 3. Switch to new pipeline when confident
```

#### Phase 4: Decommission
```bash
# 1. Stop routing traffic to old system
# 2. Shutdown old application
# 3. Remove old codebase
```

### Strategy 2: Big Bang Migration

Complete migration in a single deployment window.

#### Prerequisites
- [ ] Database backup completed
- [ ] Rollback plan documented
- [ ] All services tested in staging
- [ ] Client applications notified of maintenance window

#### Migration Steps
```bash
# 1. Stop the old application
sudo systemctl stop sudan-news-app

# 2. Backup database
pg_dump news_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Run database migrations
cd shared_models
alembic upgrade head

# 4. Start new services
cd ../sudan-news-api
docker-compose up -d

cd ../sudan-news-pipeline
docker-compose up -d

# 5. Update reverse proxy configuration
# Point all traffic to sudan-news-api

# 6. Test system functionality
curl "http://your-domain/api/clusters"
curl "http://your-domain/health"

# 7. Update DNS/client configurations if needed
```

## Environment Configuration

### Database Migration

The new schema is backwards compatible. Existing data remains accessible.

```bash
# For PostgreSQL
export DATABASE_URL="postgresql://user:pass@host:5432/news_db"

# For SQLite (development)
export DATABASE_URL="sqlite:///news_aggregator.db"
```

### Service Configuration

#### API Service (.env)
```bash
DATABASE_URL=postgresql://user:pass@host:5432/news_db
FLASK_ENV=production
SECRET_KEY=your-production-secret
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
```

#### Pipeline Service (.env)
```bash
DATABASE_URL=postgresql://user:pass@host:5432/news_db
GOOGLE_API_KEY=your-genai-key
HF_TOKEN=your-huggingface-token
EMBEDDING_MODEL=google/embeddinggemma-300m
SIMILARITY_THRESHOLD=0.5
LOG_LEVEL=INFO
```

## Docker Deployment

### Single-Compose Setup
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
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: ./sudan-news-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://news_user:news_pass@db:5432/news_db
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  pipeline:
    build: ./sudan-news-pipeline
    environment:
      - DATABASE_URL=postgresql://news_user:news_pass@db:5432/news_db
    depends_on:
      - db
      - api
    # Run on schedule or trigger

volumes:
  postgres_data:
```

### Kubernetes Deployment

#### API Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sudan-news-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sudan-news-api
  template:
    metadata:
      labels:
        app: sudan-news-api
    spec:
      containers:
      - name: api
        image: sudan-news-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: database-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

#### Pipeline CronJob
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: sudan-news-pipeline
spec:
  schedule: "*/30 * * * *"  # Every 30 minutes
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: pipeline
            image: sudan-news-pipeline:latest
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: database-url
            command: ["python", "src/run_pipeline.py", "run-once"]
          restartPolicy: OnFailure
```

## Monitoring & Observability

### Health Checks
```bash
# API health
curl "https://your-domain/health"

# Database connectivity
curl "https://your-domain/api/clusters?page=1&limit=1"

# Pipeline status (implement endpoint)
curl "https://pipeline.your-domain/health"
```

### Logging
```bash
# API logs
docker logs sudan-news-api

# Pipeline logs
docker logs sudan-news-pipeline

# Database logs
docker logs postgres
```

### Metrics to Monitor
- API response times (< 500ms)
- Pipeline execution duration (< 10 minutes)
- Database connection pool usage
- Error rates (< 1%)
- Memory/CPU usage per service

## Rollback Procedures

### Emergency Rollback
```bash
# 1. Stop new services
docker-compose down

# 2. Restore old application
sudo systemctl start sudan-news-app

# 3. Restore database if needed
psql news_db < backup_file.sql

# 4. Update reverse proxy to old service
```

### Gradual Rollback
```bash
# 1. Route traffic back to old API
# 2. Stop new pipeline, keep API running for reads
# 3. Monitor for issues
# 4. Complete rollback if needed
```

## Testing Migration

### Compatibility Testing
```bash
# Test API responses match exactly
diff <(curl "http://old-api/api/clusters") <(curl "http://new-api/api/clusters")

# Test web interface renders correctly
curl "http://new-api/" | grep -q "الأحداث المجمعة"

# Test mobile app integration
# Use same API calls as production app
```

### Performance Testing
```bash
# Load testing
ab -n 1000 -c 10 "http://new-api/api/clusters?page=1&limit=50"

# Compare response times
time curl "http://old-api/api/clusters"
time curl "http://new-api/api/clusters"
```

### Data Integrity Testing
```bash
# Compare article counts
old_count=$(curl "http://old-api/api/articles" | jq '. | length')
new_count=$(curl "http://new-api/api/articles" | jq '. | length')

if [ "$old_count" -eq "$new_count" ]; then
    echo "Data integrity verified"
else
    echo "Data mismatch detected"
fi
```

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
cd shared_models
python -c "from db import get_session; s = next(get_session()); print('DB connected')"
```

#### API Not Starting
```bash
# Check logs
docker logs sudan-news-api

# Test configuration
cd sudan-news-api
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DATABASE_URL'))"
```

#### Pipeline Not Processing
```bash
# Check API keys
cd sudan-news-pipeline
python -c "import os; print('GOOGLE_API_KEY:', bool(os.getenv('GOOGLE_API_KEY')))"

# Test RSS feeds
curl "https://sudanile.com/rss" | head -20
```

### Performance Issues

#### Slow API Responses
- Check database indexes
- Monitor connection pool usage
- Enable query logging

#### High Memory Usage
- Monitor Gunicorn worker processes
- Check for memory leaks in pipeline
- Adjust Docker memory limits

#### Database Bottlenecks
- Monitor slow queries
- Check connection pool settings
- Consider read replicas

## Post-Migration Tasks

### Optimization
1. **Enable Caching**: Add Redis for API response caching
2. **Database Tuning**: Optimize indexes for new query patterns
3. **Monitoring Setup**: Implement comprehensive monitoring
4. **Backup Strategy**: Update backup procedures for new architecture

### Feature Migration
1. **Push Notifications**: Migrate to new token management system
2. **User Management**: Implement user authentication if needed
3. **Analytics**: Add usage tracking and reporting
4. **Admin Interface**: Build admin dashboard for new architecture

### Team Training
1. **Developer Onboarding**: Train team on new architecture
2. **Deployment Procedures**: Document new deployment workflows
3. **Monitoring Dashboards**: Setup monitoring and alerting
4. **Incident Response**: Update incident response procedures

## Success Metrics

### Technical Metrics
- ✅ **Zero Downtime**: Migration completed without service interruption
- ✅ **Performance**: API response times within 10% of original
- ✅ **Data Integrity**: All existing data preserved and accessible
- ✅ **Compatibility**: All client applications work unchanged

### Business Metrics
- ✅ **Scalability**: Independent scaling of pipeline and API
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **Development Velocity**: Parallel development on services
- ✅ **Reliability**: Improved error handling and monitoring

## Support

For migration assistance:
- Review `DELIVERABLES.md` for complete system documentation
- Check component READMEs for service-specific instructions
- Monitor health endpoints during migration
- Have rollback procedures ready

The migration is designed to be safe and reversible at any point.
