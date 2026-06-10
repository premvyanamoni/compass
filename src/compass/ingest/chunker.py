from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from compass.config import Config

def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_text(text)

def chunk_text_semantic(text:str, config:Config) -> list[str]:
    huggingFaceEmbeddings = HuggingFaceEmbeddings(model_name=config.sentence_transformer_model_name)
    splitter = SemanticChunker(embeddings=huggingFaceEmbeddings)
    return splitter.split_text(text=text)