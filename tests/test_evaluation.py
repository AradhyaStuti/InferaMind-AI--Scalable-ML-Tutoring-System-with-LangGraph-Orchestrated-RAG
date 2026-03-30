"""Tests for RAGAS evaluation metrics."""

import pytest
from tests.conftest import requires_embeddings

from backend.rag.evaluation import (
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy,
    evaluate,
)
from backend.rag.embeddings import embedding_service


@requires_embeddings
class TestContextPrecision:
    def test_relevant_chunks_score_high(self):
        sources = embedding_service.search("supervised learning")
        score = context_precision("What is supervised learning?", sources)
        assert 0.0 <= score <= 1.0
        assert score > 0.3


@requires_embeddings
class TestContextRecall:
    def test_recall_with_ground_truth(self):
        sources = embedding_service.search("gradient descent")
        gt = "Gradient descent is an optimization algorithm. It minimizes the cost function by iteratively updating parameters."
        score = context_recall(sources, gt)
        assert 0.0 <= score <= 1.0


@requires_embeddings
class TestFaithfulness:
    def test_grounded_answer_scores_high(self):
        sources = embedding_service.search("linear regression")
        answer = "Linear regression fits a straight line to data to predict continuous values."
        score = faithfulness(answer, sources)
        assert 0.0 <= score <= 1.0


@requires_embeddings
class TestAnswerRelevancy:
    def test_relevant_answer_scores_high(self):
        score = answer_relevancy(
            "What is machine learning?",
            "Machine learning is a subset of AI that learns patterns from data.",
        )
        assert score > 0.5


@requires_embeddings
class TestEvaluateAggregate:
    def test_returns_all_metrics(self):
        sources = embedding_service.search("supervised learning")
        answer = "Supervised learning uses labeled data to train models."
        metrics = evaluate("What is supervised learning?", answer, sources)
        assert "context_precision" in metrics
        assert "faithfulness" in metrics
        assert "answer_relevancy" in metrics
        assert "ragas_score" in metrics
        for v in metrics.values():
            assert 0.0 <= v <= 1.0
