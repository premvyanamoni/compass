from sentence_transformers import SentenceTransformer
import voyageai

from compass.config import Config

def embed_chunks(chunks: list[str], config: Config) -> list[list[float]]:
    model = SentenceTransformer(config.sentence_transformer_model_name)
    return model.encode(chunks).tolist()

def embed_chunks_voyage(chunks: list[str], config: Config, input_type:str) -> list[list[float]]:
    vo = voyageai.Client(api_key=config.voyage_api_key)
    results = []
    for i in range(0, len(chunks), 128):
        batch = chunks[i:i+128] 
        results.extend(vo.embed(batch, model="voyage-4-large",input_type=input_type,truncation=True).embeddings)
    return results
    