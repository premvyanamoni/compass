from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    openai_api_key: str
    anthropic_api_key: str
    cohere_api_key: str
    lancedb_path: str = "data/lancedb"
    embedding_model_name: str = "text-embedding-3-small"
    sentence_transformer_model_name: str = "all-MiniLM-L6-v2"
    llm_model_name: str = "claude-sonnet-4-6"
    chunk_size: int = 1000
    chunk_overlap: int = 200