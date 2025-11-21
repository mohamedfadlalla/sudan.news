from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from ..models import Entity, Article

class EntityRepository:
    def __init__(self, session: Session):
        self.session = session

    def insert_entities(self, article_id: int, people: list = None, cities: list = None,
                       regions: list = None, countries: list = None, organizations: list = None,
                       political_parties_and_militias: list = None, brands: list = None,
                       job_titles: list = None, category: str = None) -> Entity:
        """Insert entity analysis results for an article"""
        created_at = datetime.now().isoformat()
        entity = Entity(
            article_id=article_id,
            people=people or [],
            cities=cities or [],
            regions=regions or [],
            countries=countries or [],
            organizations=organizations or [],
            political_parties_and_militias=political_parties_and_militias or [],
            brands=brands or [],
            job_titles=job_titles or [],
            category=category,
            created_at=created_at
        )
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_article_id(self, article_id: int) -> Optional[Entity]:
        """Get entities for a specific article"""
        return self.session.query(Entity).filter(Entity.article_id == article_id).first()

    def update_entities(self, article_id: int, **kwargs) -> bool:
        """Update entity data for an article"""
        entity = self.get_by_article_id(article_id)
        if not entity:
            return False

        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        self.session.commit()
        return True

    def get_entity_stats(self) -> Dict[str, Any]:
        """Get statistics about entities in the database"""
        from sqlalchemy import func

        # Count articles with entities
        total_with_entities = self.session.query(func.count(Entity.id)).scalar()

        # Most common categories
        category_counts = self.session.query(
            Entity.category, func.count(Entity.id)
        ).filter(Entity.category.isnot(None)).group_by(Entity.category).all()

        # Most common cities, people, etc. (top 10 each)
        def get_top_entities(field):
            # This is complex with JSON arrays - simplified version
            return []

        return {
            'total_articles_with_entities': total_with_entities,
            'category_distribution': dict(category_counts),
            'top_cities': get_top_entities('cities'),
            'top_people': get_top_entities('people'),
            'top_organizations': get_top_entities('organizations')
        }
