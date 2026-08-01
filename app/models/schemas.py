from pydantic import BaseModel


class AudioUploadResponse(BaseModel):
    filename: str
    status: str

class AudioStatusResponse(BaseModel):
    filename: str
    status: str

class QueryRequest(BaseModel):
    question: str
    
class Source(BaseModel):
    filename: str
    chunk: int
    
class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]
