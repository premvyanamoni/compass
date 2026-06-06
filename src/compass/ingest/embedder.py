
from sentence_transformers import SentenceTransformer

from compass.config import Config

def embed_chunks(chunks: list[str], config: Config) -> list[list[float]]:
    model = SentenceTransformer(config.sentence_transformer_model_name)
    return model.encode(chunks).tolist()
    