from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_ATLAS_USERNAME: str
    MONGODB_ATLAS_PASSWORD: str
    MONGODB_ATLAS_HOST: str
    MONGODB_ATLAS_DB_NAME: str
    MONGODB_ATLAS_MOVIES_VECTOR_SEARCH_INDEX_NAME: str

    class Config:
        env_file = '.env'


# Load settings from .env file
settings = Settings()
