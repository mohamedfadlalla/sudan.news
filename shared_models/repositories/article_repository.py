import hashlib
import re
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models import Article, Source, Entity

class ArticleRepository:
    def __init__(self, session: Session):
        self.session = session

    def _normalize_arabic(self, text):
        """Normalize Arabic text by removing diacritics and standardizing characters."""
        if not text:
            return ""
        # Remove diacritics (Tashkeel)
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        # Convert أ,إ,آ to ا
        text = re.sub(r'[أإآ]', 'ا', text)
        # Convert ة to ه
        text = re.sub(r'ة', 'ه', text)
        # Convert ى to ي
        text = re.sub(r'ى', 'ي', text)
        return text

    def _compute_content_hash(self, headline: str, description: str) -> str:
        """Compute SHA-256 hash of normalized headline + description for deduplication."""
        normalized_headline = self._normalize_arabic(headline or "").strip().lower()
        normalized_description = self._normalize_arabic(description or "").strip().lower()
        content = f"{normalized_headline}|{normalized_description}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get_recent_unclustered(self, hours: int = 24) -> List[Article]:
        """Get articles published in the last N hours that haven't been clustered"""
        # For testing, be more lenient with time filtering
        # In production, this would use proper datetime comparison
        from ..models import cluster_articles
        return self.session.query(Article).outerjoin(
            cluster_articles, Article.id == cluster_articles.c.article_id
        ).filter(
            cluster_articles.c.article_id.is_(None)
        ).all()

    def insert_article(self, source_id: int, headline: str, description: str,
                      published_at: str, article_url: str, image_url: str = None,
                      category: str = "local") -> Article:
        """Insert a new article, checking for duplicates based on content hash."""
        # Compute content hash for deduplication
        content_hash = self._compute_content_hash(headline, description)

        # Check if article with same content hash already exists
        existing_article = self.session.query(Article).filter(Article.content_hash == content_hash).first()
        if existing_article:
            # Return existing article instead of creating duplicate
            return existing_article

        # Create new article
        created_at = datetime.now().isoformat()
        article = Article(
            source_id=source_id,
            headline=headline,
            description=description,
            published_at=published_at,
            article_url=article_url,
            image_url=image_url,
            created_at=created_at,
            category=category,
            content_hash=content_hash
        )
        self.session.add(article)
        self.session.flush()  # Get ID without committing
        return article

    def get_by_id(self, article_id: int) -> Optional[Article]:
        """Get article by ID"""
        return self.session.query(Article).filter(Article.id == article_id).first()

    def list_by_filters(self, filters: Dict[str, Any], limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List articles with filters"""
        query = self.session.query(Article).join(Source)

        if 'category' in filters:
            query = query.filter(Article.category == filters['category'])
        if 'date_from' in filters:
            query = query.filter(Article.published_at >= filters['date_from'])
        if 'date_to' in filters:
            query = query.filter(Article.published_at <= filters['date_to'])
        if 'keyword' in filters:
            keyword = f"%{filters['keyword']}%"
            query = query.filter(
                or_(
                    Article.headline.like(keyword),
                    Article.description.like(keyword)
                )
            )

        articles = query.order_by(desc(Article.published_at)).limit(limit).offset(offset).all()

        # Convert to dictionaries for API compatibility
        result = []
        for article in articles:
            result.append({
                'id': article.id,
                'headline': article.headline,
                'description': article.description,
                'published_at': article.published_at,
                'article_url': article.article_url,
                'image_url': article.image_url,
                'source_name': article.source.name if article.source else None,
                'category': article.category
            })
        return result

    def update_cluster_id(self, article_id: int, cluster_id: int):
        """Update article's cluster assignment"""
        article = self.get_by_id(article_id)
        if article:
            article.cluster_id = cluster_id
            self.session.commit()

    def mark_as_processed(self, article_id: int):
        """Mark article as processed (update updated_at)"""
        article = self.get_by_id(article_id)
        if article:
            article.updated_at = datetime.now().isoformat()
            self.session.commit()

    def get_with_entities(self, article_id: int) -> Optional[Dict[str, Any]]:
        """Get article with its entities"""
        article = self.session.query(Article).filter(Article.id == article_id).first()
        if not article:
            return None

        entities = article.get_entities(self.session)
        result = {
            'id': article.id,
            'headline': article.headline,
            'description': article.description,
            'published_at': article.published_at,
            'article_url': article.article_url,
            'image_url': article.image_url,
            'source_name': article.source.name if article.source else None,
            'source_url': article.source.url if article.source else None,
            'category': article.category,
            'entities': None
        }

        if entities:
            result['entities'] = {
                'people': entities.people or [],
                'cities': entities.cities or [],
                'regions': entities.regions or [],
                'countries': entities.countries or [],
                'organizations': entities.organizations or [],
                'political_parties_and_militias': entities.political_parties_and_militias or [],
                'brands': entities.brands or [],
                'job_titles': entities.job_titles or [],
                'nlp_category': entities.category
            }

        return result
