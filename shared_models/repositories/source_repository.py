from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Source

class SourceRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_or_create_source(self, url: str, name: str = None, language: str = 'ar', bias: str = None) -> Source:
        """Get existing source or create new one"""
        source = self.session.query(Source).filter(Source.url == url).first()
        if source:
            return source

        if not name:
            name = url  # Use URL as name if not provided

        source = Source(name=name, url=url, language=language, bias=bias)
        self.session.add(source)
        self.session.flush()
        return source

    def get_by_id(self, source_id: int) -> Optional[Source]:
        """Get source by ID"""
        return self.session.query(Source).filter(Source.id == source_id).first()

    def get_by_url(self, url: str) -> Optional[Source]:
        """Get source by URL"""
        return self.session.query(Source).filter(Source.url == url).first()

    def get_all_sources(self) -> List[Source]:
        """Get all sources"""
        return self.session.query(Source).all()

    def update_source(self, source_id: int, name: str = None, language: str = None) -> bool:
        """Update source information"""
        source = self.get_by_id(source_id)
        if not source:
            return False

        if name is not None:
            source.name = name
        if language is not None:
            source.language = language

        self.session.commit()
        return True

    def get_source_details(self, source_id: int, limit: int = 20):
        """Get source details with recent articles"""
        from ..models import Article
        from sqlalchemy import desc
        
        source = self.get_by_id(source_id)
        if not source:
            return None
        
        # Get recent articles from this source
        recent_articles = self.session.query(Article).filter(
            Article.source_id == source_id
        ).order_by(desc(Article.published_at)).limit(limit).all()
        
        return {
            'id': source.id,
            'name': source.name,
            'url': source.url,
            'language': source.language,
            'owner': source.owner,
            'founded_at': source.founded_at,
            'hq_location': source.hq_location,
            'bias': source.bias,
            'recent_articles': [{
                'id': article.id,
                'headline': article.headline,
                'description': article.description,
                'published_at': article.published_at,
                'article_url': article.article_url,
                'image_url': article.image_url,
                'category': article.category
            } for article in recent_articles],
            'total_articles': len(source.articles) if hasattr(source, 'articles') else 0
        }
