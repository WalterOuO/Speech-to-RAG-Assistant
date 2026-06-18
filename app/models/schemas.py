from pydantic import BaseModel


class AudioUploadResponse(BaseModel):
    filename: str
    status: str

class AudioStatusResponse(BaseModel):
    filename: str
    status: str

class QueryRequest(BaseModel):
    filename: str
    question: str
    top_k: int
    

class QueryResponse(BaseModel):
    filename: str
    question: str
    answer: str
    sources: list[Source]
