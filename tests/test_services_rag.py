import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from app.services import rag_service

def test_rerank_documents_empty():
    assert rag_service.rerank_documents("q", []) == []

def test_rerank_documents_sorting():
    docs = [Document(page_content="A"), Document(page_content="B")]
    # Mock reranker.predict to return scores [0.1, 0.9]
    with patch("app.services.rag_service.reranker") as mock_rerank:
        mock_rerank.predict.return_value = [0.1, 0.9]
        result = rag_service.rerank_documents("q", docs)
        assert result[0].page_content == "B"
        assert len(result) == 2

def test_ask_question_no_docs():
    with patch("app.services.rag_service.build_hybrid_retriever") as mock_build_retriever:
        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = []
        mock_build_retriever.return_value = mock_retriever
        
        res = rag_service.ask_question("Any question?")
        assert res["answer"] == "在該文件中找不到相關參考資料。"
        assert res["sources"] == []

def test_ask_question_success():
    docs = [Document(page_content="The capital of France is Paris", metadata={"source": "geo.wav"})]
    with patch("app.services.rag_service.build_hybrid_retriever") as mock_build_retriever, \
         patch("app.services.rag_service.rerank_documents") as mock_rerank, \
         patch("app.services.rag_service.llm") as mock_llm:

        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = docs
        mock_build_retriever.return_value = mock_retriever

        mock_rerank.return_value = docs
        mock_llm.invoke.return_value = "Paris is the capital."

        res = rag_service.ask_question("What is the capital of France?")
        assert res["answer"] == "Paris is the capital."
        assert res["sources"][0]["filename"] == "geo.wav"

def test_ask_question_llm_error():
    docs = [Document(page_content="Some text")]
    with patch("app.services.rag_service.build_hybrid_retriever") as mock_build_retriever, \
         patch("app.services.rag_service.rerank_documents") as mock_rerank, \
         patch("app.services.rag_service.llm") as mock_llm:

        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = docs
        mock_build_retriever.return_value = mock_retriever

        mock_rerank.return_value = docs
        mock_llm.invoke.side_effect = Exception("Ollama Down")

        with pytest.raises(HTTPException) as exc:
            rag_service.ask_question("q")
        assert exc.value.status_code == 500
        assert "Ollama 呼叫失敗" in exc.value.detail