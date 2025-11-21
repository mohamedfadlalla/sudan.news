from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.types import TypeDecorator
import json
from typing import Any, Dict, List

Base = declarative_base()

class JSONType(TypeDecorator):
    """Custom JSON type that works with both PostgreSQL and SQLite"""
    impl = Text

    def process_bind_param(self, value: Any, dialect) -> str:
        if value is None:
            return None
        if dialect.name == 'postgresql':
            # PostgreSQL has native JSON support
            return value
        # For SQLite, serialize to JSON string
        return json.dumps(value, ensure_ascii=False)

    def process_result_value(self, value: Any, dialect) -> Any:
        if value is None:
            return None
        if dialect.name == 'postgresql':
            # PostgreSQL returns JSON objects directly
            return value
        # For SQLite, parse JSON string
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

# Association table for many-to-many relationship
cluster_articles = Table(
    'cluster_articles',
    Base.metadata,
    Column('cluster_id', Integer, ForeignKey('clusters.id'), primary_key=True),
    Column('article_id', Integer, ForeignKey('articles.id'), primary_key=True),
    Column('similarity_score', Float)
)

class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    url = Column(String)
    language = Column(String)
    owner = Column(String)
    founded_at = Column(String)
    hq_location = Column(String)
    bias = Column(String)

    # Relationship
    articles = relationship("Article", back_populates="source")

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('sources.id'))
    headline = Column(Text)
    description = Column(Text)
    published_at = Column(String)  # Stored as ISO string
    article_url = Column(String)
    image_url = Column(String)
    created_at = Column(String)
    updated_at = Column(String)
    category = Column(String)  # 'local' or 'international'

    # Relationships
    source = relationship("Source", back_populates="articles")
    clusters = relationship("Cluster", secondary=cluster_articles, back_populates="articles")
    entities = relationship("Entity", back_populates="article", uselist=False)

    def get_entities(self, session) -> 'Entity':
        """Get entities for this article"""
        return session.query(Entity).filter(Entity.article_id == self.id).first()

class Cluster(Base):
    __tablename__ = 'clusters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text)
    number_of_sources = Column(Integer)
    published_at = Column(String)
    created_at = Column(String)

    # New columns for Blindspot and Trending features
    blindspot_type = Column(String)
    bias_coverage_pro = Column(Integer, default=0)
    bias_coverage_neutral = Column(Integer, default=0)
    bias_coverage_oppose = Column(Integer, default=0)
    bias_balance_score = Column(Float, default=0.0)
    
    coverage_velocity = Column(Float, default=0.0)
    is_trending = Column(Integer, default=0) # Boolean in SQLite is usually 0/1
    first_seen_at = Column(String)
    last_coverage_check = Column(String)
    coverage_history = Column(JSONType, default=dict)

    # Relationships
    articles = relationship("Article", secondary=cluster_articles, back_populates="clusters")

    def add_article(self, session, article: Article, score: float):
        """Add an article to this cluster with similarity score"""
        from sqlalchemy import insert
        stmt = insert(cluster_articles).values(
            cluster_id=self.id,
            article_id=article.id,
            similarity_score=score
        )
        session.execute(stmt)

class Entity(Base):
    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('articles.id'))
    people = Column(JSONType, default=list)
    cities = Column(JSONType, default=list)
    regions = Column(JSONType, default=list)
    countries = Column(JSONType, default=list)
    organizations = Column(JSONType, default=list)
    political_parties_and_militias = Column(JSONType, default=list)
    brands = Column(JSONType, default=list)
    job_titles = Column(JSONType, default=list)
    category = Column(String)  # NLP category like 'سياسة'
    created_at = Column(String)

    # Relationship
    article = relationship("Article", back_populates="entities")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    email = Column(String)
    created_at = Column(String)

    # Relationship
    tokens = relationship("UserToken", back_populates="user")

class UserToken(Base):
    __tablename__ = 'user_tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    device_id = Column(String)
    token = Column(String)
    platform = Column(String)  # 'android' or 'ios'
    created_at = Column(String)
    updated_at = Column(String)

    # Relationship
    user = relationship("User", back_populates="tokens")
