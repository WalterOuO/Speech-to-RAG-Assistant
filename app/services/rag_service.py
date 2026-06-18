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

def ask_question(filename, question):
    relevant_docs = vector_store.similarity_search(
        question,
        k=4,
        filter={"source_file": filename}
    )
                            
    if not relevant_docs:
        return {"filename": filename,
                "question": question,
                "answer": "在該文件中找不到相關參考資料。"
                }

    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    prompt = build_prompt(context, question)

    try:
        answer = str(llm.invoke(prompt))
        return {
            "filename": filename,
            "question": question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama 呼叫失敗: {str(e)}")
