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


# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
# UPLOAD_DIR = os.path.join(BASE_DIR, "transcripts")


# def upload_transcript(file):
#     if not file.filename.endswith(".txt"):
#         raise HTTPException(status_code=400, detail="只支援 TXT 檔案上傳")

#     filename = file.filename
#     saved_txt_path = os.path.join(UPLOAD_DIR, filename)

#     with open(saved_txt_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     existing_docs = vector_store.get(
#         where={"source_file": filename},
#         limit=1
#     )

#     if len(existing_docs["ids"]) > 0:
#         return {
#             "message": f"{filename} 已寫入過資料庫",
#             "filename": filename
#         }

#     print(f"正在處理新檔案：{filename}...")
#     try:
#         with open(saved_txt_path, "r", encoding="utf-8") as f:
#             text = f.read()

#         docs = [Document(page_content=text, metadata={"source_file": filename})]

#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200,
#             add_start_index=True,
#         )
#         chunks = text_splitter.split_documents(docs)

#         for chunk in chunks:
#             chunk.metadata["source_audio"] = filename

#         vector_store.add_documents(chunks)

#         print(f"{filename} Embedding 寫入成功！")

#         return {
#             "message": f"{filename} 上傳並成功建立向量索引！",
#             "filename": filename
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"解析 TXT 檔案失敗: {str(e)}")




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
