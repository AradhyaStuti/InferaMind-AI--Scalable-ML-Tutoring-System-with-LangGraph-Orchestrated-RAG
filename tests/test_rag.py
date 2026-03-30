"""Test RAG pipeline — embeddings, graph, and classifier."""

import pytest
from tests.conftest import requires_embeddings

from backend.rag.embeddings import embedding_service
from backend.rag.graph import classify_node


@requires_embeddings
class TestEmbeddingService:
    def test_embeddings_loaded(self):
        assert embedding_service.df is not None
        assert len(embedding_service.df) > 0

    def test_search_returns_results(self):
        results = embedding_service.search("supervised learning")
        assert len(results) > 0
        assert len(results) <= 5

    def test_search_result_structure(self):
        results = embedding_service.search("gradient descent")
        for r in results:
            assert "video" in r
            assert "text" in r
            assert "start" in r
            assert "end" in r
            assert "similarity" in r
            assert isinstance(r["similarity"], float)
            assert 0 <= r["similarity"] <= 1


@requires_embeddings
class TestGraphClassifier:
    def test_classify_course_related(self):
        state = {
            "question": "What is supervised learning?",
            "chat_history": [],
            "sources": [],
            "query_type": "",
        }
        result = classify_node(state)
        assert result["query_type"] == "course_related"

    def test_classify_off_topic(self):
        state = {
            "question": "What is the best recipe for chocolate cake?",
            "chat_history": [],
            "sources": [],
            "query_type": "",
        }
        result = classify_node(state)
        assert result["query_type"] == "off_topic"
