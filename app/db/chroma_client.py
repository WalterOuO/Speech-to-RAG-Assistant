import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
from app.config import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, "chroma_langchain_db")


embeddings = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL
)

vector_store = Chroma(
    collection_name="speech_rag_collection",
    embedding_function=embeddings,
    persist_directory=DB_PATH,
)

llm = Ollama(
    model=settings.OLLAMA_MODEL,
    base_url="http://ollama:11434"
    )


def get_vector_store():
    return vector_store


def get_llm():
    return llm