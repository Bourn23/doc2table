from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # The default value points to a local SQLite file named `lumina.db`
    DATABASE_URL: str = "sqlite+aiosqlite:///./lumina.db"
    # Add the API keys here
    NVIDIA_EMBED_API_KEY: str
    NVIDIA_RERANK_API_KEY: str
    GOOGLE_GEMINI_API_KEY: str
    NVIDIA_API_KEY: str
    NVIDIA_NIM_API_KEY: str
    
    # Graph database settings
    NEO4J_URL: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str
    
    # graph LLM model
    GRAPH_LLM_MODEL: str
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

print(f"[database] Using DATABASE_URL={settings.DATABASE_URL}")

# The async engine is the entry point to the database
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # set True to debug SQL
)

# This creates a session factory that we will use to get a database session
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# This is the base class that our ORM models will inherit from
Base = declarative_base()

# Dependency for FastAPI to get a DB session
async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db