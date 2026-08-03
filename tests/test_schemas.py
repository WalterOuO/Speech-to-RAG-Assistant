import pytest
from app.models import schemas

def test_audio_upload_response():
    resp = schemas.AudioUploadResponse(filename="test.wav", status="processing")
    assert resp.filename == "test.wav"
    assert resp.status == "processing"

def test_query_request():
    req = schemas.QueryRequest(question="Hello?")
    assert req.question == "Hello?"

def test_query_response():
    source = schemas.Source(filename="test.wav", chunk=1)
    resp = schemas.QueryResponse(
        question="Hello?",
        answer="Hi!",
        sources=[source]
    )
    assert resp.answer == "Hi!"
    assert resp.sources[0].filename == "test.wav"
