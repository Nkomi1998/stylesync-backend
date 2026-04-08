import asyncio
from sqlalchemy import create_engine, MetaData, Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/stylesync")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class ScrapedSite(Base):
    __tablename__ = "scraped_sites"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    html_snapshot = Column(String, nullable=True)
    extraction_status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DesignToken(Base):
    __tablename__ = "design_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("scraped_sites.id"))
    colors = Column(JSON, nullable=True)
    typography = Column(JSON, nullable=True)
    spacing = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LockedToken(Base):
    __tablename__ = "locked_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, ForeignKey("design_tokens.id"))
    token_type = Column(String)
    token_key = Column(String)
    locked_value = Column(JSON)
    user_id = Column(String, nullable=True)

class VersionHistory(Base):
    __tablename__ = "version_history"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, ForeignKey("design_tokens.id"))
    before_state = Column(JSON)
    after_state = Column(JSON)
    change_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

