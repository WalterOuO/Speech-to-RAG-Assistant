import os
import shutil
from fastapi import HTTPException
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .prompt import build_prompt 
from app.db.chroma_client import (
    get_vector_store,
    get_llm
)

vector_store = get_vector_store()
llm = get_llm()

def ask_question(filename, question, top_k=4):
    relevant_docs = vector_store.similarity_search(
        question,
        k=top_k,
        filter={"source_file": filename}
    )
                            
    if not relevant_docs:
        return {"filename": filename,
                "question": question,
                "answer": "在該文件中找不到相關參考資料。"
                }
    
    context = ""
    sources = []
    for idx, doc in enumerate(relevant_docs):
        context += f"\n[Chunk {idx+1}]\n{doc.page_content}\n"
    
        sources.append({
            "filename": doc.metadata.get("source_audio"),
            "chunk": idx + 1
        })

    prompt = build_prompt(context, question)

    try:
        answer = str(llm.invoke(prompt))
        return {
            "filename": filename,
            "question": question,
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama 呼叫失敗: {str(e)}")
