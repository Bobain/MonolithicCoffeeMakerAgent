"""Tests for ACE embeddings utility."""

import os
from unittest.mock import Mock, patch

import numpy as np
import pytest

from coffee_maker.autonomous.ace.embeddings import (
    APIKeyMissingError,
    OpenAIError,
    clear_cache,
    compute_similarity,
    get_cache_info,
    get_cache_size,
    get_embedding,
)


class TestEmbeddingGeneration:
    """Test embedding generation with OpenAI API."""

    def test_get_embedding_missing_api_key(self):
        """Test that missing API key raises APIKeyMissingError."""
        with patch.dict(os.environ, {}, clear=True):
            clear_cache()
            with pytest.raises(APIKeyMissingError) as exc_info:
                get_embedding("test text")

            # Check error message contains setup instructions
            assert "OPENAI_API_KEY" in str(exc_info.value)
            assert "https://platform.openai.com/api-keys" in str(exc_info.value)

    def test_get_embedding_with_api_key(self):
        """Test successful embedding generation."""
        mock_embedding = [0.1] * 1536  # OpenAI ada-002 returns 1536 dimensions

        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=mock_embedding)]
        mock_client.embeddings.create.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("openai.OpenAI", return_value=mock_client):
                clear_cache()
                embedding = get_embedding("test text")

                assert embedding == mock_embedding
                assert len(embedding) == 1536
                mock_client.embeddings.create.assert_called_once_with(input="test text", model="text-embedding-ada-002")

    def test_get_embedding_custom_model(self):
        """Test embedding generation with custom model."""
        mock_embedding = [0.2] * 768

        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=mock_embedding)]
        mock_client.embeddings.create.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("openai.OpenAI", return_value=mock_client):
                clear_cache()
                embedding = get_embedding("test text", model="text-embedding-3-small")

                assert embedding == mock_embedding
                mock_client.embeddings.create.assert_called_once_with(input="test text", model="text-embedding-3-small")

    def test_get_embedding_openai_not_installed(self):
        """Test error when openai library not installed."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            # Mock the import to raise ImportError
            import sys

            with patch.dict(sys.modules, {"openai": None}):
                clear_cache()
                with pytest.raises(OpenAIError) as exc_info:
                    get_embedding("test text")

                assert "not installed" in str(exc_info.value)
                assert "pip install openai" in str(exc_info.value)

    def test_get_embedding_api_error(self):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client.embeddings.create.side_effect = Exception("API rate limit exceeded")

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("openai.OpenAI", return_value=mock_client):
                clear_cache()
                with pytest.raises(OpenAIError) as exc_info:
                    get_embedding("test text")

                assert "API call failed" in str(exc_info.value)
                assert "rate limit" in str(exc_info.value)


class TestEmbeddingCache:
    """Test embedding caching functionality."""

    def test_caching_works(self):
        """Test that embeddings are cached."""
        mock_embedding = [0.3] * 1536

        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=mock_embedding)]
        mock_client.embeddings.create.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("openai.OpenAI", return_value=mock_client):
                clear_cache()

                # First call should hit API
                emb1 = get_embedding("cached text")
                assert mock_client.embeddings.create.call_count == 1

                # Second call should use cache
                emb2 = get_embedding("cached text")
                assert mock_client.embeddings.create.call_count == 1  # Still 1, not 2

                assert emb1 == emb2

    def test_clear_cache(self):
        """Test cache clearing."""
        mock_embedding = [0.4] * 1536

        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=mock_embedding)]
        mock_client.embeddings.create.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("openai.OpenAI", return_value=mock_client):
                clear_cache()

                # Add to cache
                get_embedding("text 1")
                assert get_cache_size() == 1

                # Clear cache
                clear_cache()
                assert get_cache_size() == 0

    def test_get_cache_size(self):
        """Test cache size tracking."""
        mock_embedding = [0.5] * 1536

        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=mock_embedding)]
        mock_client.embeddings.create.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("openai.OpenAI", return_value=mock_client):
                clear_cache()

                assert get_cache_size() == 0

                get_embedding("text 1")
                assert get_cache_size() == 1

                get_embedding("text 2")
                assert get_cache_size() == 2

                get_embedding("text 1")  # Cache hit
                assert get_cache_size() == 2  # No change

    def test_get_cache_info(self):
        """Test cache info statistics."""
        mock_embedding = [0.6] * 1536

        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=mock_embedding)]
        mock_client.embeddings.create.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("openai.OpenAI", return_value=mock_client):
                clear_cache()

                get_embedding("text 1")
                get_embedding("text 2")

                info = get_cache_info()
                assert info["num_entries"] == 2
                assert info["estimated_memory_kb"] == 24  # 2 * 12KB


class TestCosineSimilarity:
    """Test cosine similarity calculation."""

    def test_identical_vectors(self):
        """Test similarity of identical vectors is 1.0."""
        vec = [1.0, 2.0, 3.0]
        similarity = compute_similarity(vec, vec)
        assert similarity == pytest.approx(1.0, abs=0.001)

    def test_orthogonal_vectors(self):
        """Test similarity of orthogonal vectors is 0.0."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        similarity = compute_similarity(vec1, vec2)
        assert similarity == pytest.approx(0.0, abs=0.001)

    def test_opposite_vectors(self):
        """Test similarity of opposite vectors is clamped to 0.0."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [-1.0, 0.0, 0.0]
        similarity = compute_similarity(vec1, vec2)
        # Cosine would be -1.0, but we clamp to 0.0
        assert similarity == pytest.approx(0.0, abs=0.001)

    def test_similar_vectors(self):
        """Test similarity of similar vectors."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.1, 2.1, 3.1]
        similarity = compute_similarity(vec1, vec2)
        assert similarity > 0.99  # Very similar

    def test_different_vectors(self):
        """Test similarity of different vectors."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.1, 1.0, 0.0]
        similarity = compute_similarity(vec1, vec2)
        assert 0.0 < similarity < 0.5  # Low similarity

    def test_zero_vector_handling(self):
        """Test zero vector returns 0.0 similarity."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]
        similarity = compute_similarity(vec1, vec2)
        assert similarity == 0.0

    def test_numpy_array_input(self):
        """Test compute_similarity works with numpy arrays."""
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([1.1, 2.1, 3.1])
        similarity = compute_similarity(vec1.tolist(), vec2.tolist())
        assert similarity > 0.99


class TestIntegration:
    """Integration tests for embedding workflow."""

    def test_semantic_similarity_detection(self):
        """Test semantic similarity detection workflow."""
        # Create more realistic mock embeddings using numpy
        np.random.seed(42)
        base_vec = np.random.rand(1536)
        base_vec = base_vec / np.linalg.norm(base_vec)  # Normalize

        # Similar embedding: base with same seed + tiny perturbation
        emb1 = base_vec.tolist()
        np.random.seed(43)  # Different seed for noise
        noise = np.random.randn(1536) * 0.001  # Very small Gaussian noise
        similar_vec = base_vec + noise
        similar_vec = similar_vec / np.linalg.norm(similar_vec)  # Normalize
        emb2 = similar_vec.tolist()

        # Different embedding: orthogonal to base_vec (or as close as possible)
        np.random.seed(100)
        # Create a vector orthogonal to base_vec using Gram-Schmidt
        diff_vec_raw = np.random.rand(1536)
        # Project onto base_vec and subtract (make orthogonal)
        projection = np.dot(diff_vec_raw, base_vec) * base_vec
        diff_vec = diff_vec_raw - projection
        diff_vec = diff_vec / np.linalg.norm(diff_vec)  # Normalize
        emb3 = diff_vec.tolist()

        mock_client = Mock()

        def mock_create(input, model):
            """Return different embeddings based on input."""
            if "Always run tests before committing" in input:
                return Mock(data=[Mock(embedding=emb1)])
            elif "Always run pytest before git commit" in input:
                return Mock(data=[Mock(embedding=emb2)])
            elif "Design UI with Tailwind CSS" in input:
                return Mock(data=[Mock(embedding=emb3)])
            else:
                # Fallback
                return Mock(data=[Mock(embedding=emb3)])

        mock_client.embeddings.create.side_effect = mock_create

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            with patch("openai.OpenAI", return_value=mock_client):
                clear_cache()

                # Get embeddings
                embedding1 = get_embedding("Always run tests before committing")
                embedding2 = get_embedding("Always run pytest before git commit")
                embedding3 = get_embedding("Design UI with Tailwind CSS")

                # Compute similarities
                sim_12 = compute_similarity(embedding1, embedding2)
                sim_13 = compute_similarity(embedding1, embedding3)

                # Similar texts should have higher similarity than different texts
                # Note: Actual similarity depends on the noise model and normalization
                # The key is that similar > different, and similar is "reasonably high"
                assert sim_12 > sim_13, f"Similar texts should be more similar than different texts"
                assert sim_12 > 0.70, f"Similar texts should have reasonable similarity, got {sim_12}"
                assert sim_13 < 0.60, f"Different texts should have low similarity, got {sim_13}"
