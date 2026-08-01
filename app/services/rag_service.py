import os
import shutil
from fastapi import HTTPException
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

from .prompt import build_prompt 
from app.db.chroma_client import (
    get_vector_store,
    get_llm, 
    get_reranker
)

vector_store = get_vector_store()
llm = get_llm()
reranker = get_reranker()


def build_hybrid_retriever():
    """
    Build Hybrid Retriever:
    1. Dense Vector Search
    2. BM25 Keyword Search
    """

    # 1. Dense Vector Retriever
    vector_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 20
        }
    )

    # get all documents and their metadata from the vector store
    data = vector_store.get(include=["documents", "metadatas"])

    documents = []

    for content, metadata in zip(data["documents"], data["metadatas"]):
        documents.append(
            Document(
                page_content=content,
                metadata=metadata or {}
            )
        )

    # 2. BM25 Retriever
    bm25_retriever = BM25Retriever.from_documents(documents)
    
    bm25_retriever.k = 20

    # Hybrid Search
    hybrid_retriever = EnsembleRetriever(
        retrievers=[
            bm25_retriever,
            vector_retriever
        ],
        weights=[
            0.5,
            0.5
        ]
    )

    return hybrid_retriever


# Create Hybrid Retriever
hybrid_retriever = build_hybrid_retriever()



def rerank_documents(question, documents, top_k=5):
    """
    Rerank documents using CrossEncoder
    """
    if not documents:
        return []
    

    cross_encoder_input = [(question, doc.page_content) for doc in documents]

    # Get scores from the CrossEncoder
    scores = reranker.predict(cross_encoder_input)

    # Combine documents with their scores
    scored_documents = list(zip(documents, scores))

    # Sort documents based on scores in descending order
    scored_documents.sort(key=lambda x: x[1], reverse=True)

    # Select top_k documents
    top_documents = [doc for doc, score in scored_documents[:top_k]]

    return top_documents


def ask_question(question):
    hybrid_docs = hybrid_retriever.invoke(question)
                            
    if not hybrid_docs:
        return {"question": question,
                "answer": "在該文件中找不到相關參考資料。",
                "sources": []
                }
    
    relevant_docs = rerank_documents(question, hybrid_docs, top_k=5)
    
    if not relevant_docs:
        return {"question": question,
                "answer": "在該文件中找不到相關參考資料。",
                "sources": []
                }
    
    # add source information to the response
    context = ""
    sources = []
    for idx, doc in enumerate(relevant_docs):
        context += f"\n[Chunk {idx+1}]\n{doc.page_content}\n"
    
        sources.append({
            "filename": doc.metadata.get("source_audio") or
                        doc.metadata.get("source_audio") or
                        doc.metadata.get("source"),
            "chunk": idx + 1
        })

    prompt = build_prompt(context, question)

    # Generate Answer using LLM
    try:
        answer = str(llm.invoke(prompt))
        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama 呼叫失敗: {str(e)}")
