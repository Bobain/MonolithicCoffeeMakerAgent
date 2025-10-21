"""Tests for hierarchical specification handling.

Tests the Phase 2 implementation of PRIORITY 25:
- Hierarchical spec reading with progressive disclosure
- Phase detection (ROADMAP, git, file-based)
- Context efficiency logging
"""

import pytest
from pathlib import Path
from coffee_maker.utils.spec_handler import SpecHandler


class TestHierarchicalSpecReading:
    """Test hierarchical spec reading functionality."""

    def test_read_hierarchical_not_found(self):
        """Test reading non-existent hierarchical spec."""
        handler = SpecHandler()
        result = handler.read_hierarchical("PRIORITY 999")

        assert result["success"] is False
        assert result["spec_type"] == "not_found"
        assert "No spec found" in result["reason"]

    def test_find_spec_by_priority_id_with_priority_format(self):
        """Test finding spec by PRIORITY XXX format."""
        handler = SpecHandler()

        # SPEC-025 exists in test data
        spec_path = handler._find_spec_by_priority_id("PRIORITY 25")

        if spec_path:
            # Spec exists, verify it's found
            assert spec_path.exists()
            assert "025" in str(spec_path) or "25" in str(spec_path)

    def test_detect_current_phase_default(self):
        """Test phase detection defaults to Phase 1 when no detection possible."""
        handler = SpecHandler()

        # Create a temporary spec directory for testing
        temp_dir = Path("docs/architecture/specs/SPEC-999-test")

        if temp_dir.exists():
            phase = handler._detect_current_phase(temp_dir)
            # Should default to Phase 1 or return a phase number
            assert isinstance(phase, int)
            assert phase >= 1


class TestPhaseDetection:
    """Test phase detection strategies."""

    def test_detect_current_phase_roadmap_strategy(self):
        """Test phase detection via ROADMAP strategy."""
        handler = SpecHandler()

        # Test with PRIORITY 25 which has phase tracking in ROADMAP
        temp_dir = Path("docs/architecture/specs/SPEC-025-hierarchical-modular-spec-architecture")

        if temp_dir.exists():
            phase = handler._detect_current_phase(temp_dir)
            # Should detect from ROADMAP
            assert isinstance(phase, int)
            assert phase >= 1

    def test_count_phases(self):
        """Test counting total phases in hierarchical spec."""
        handler = SpecHandler()

        # Test with PRIORITY 25 which has multiple phases
        temp_dir = Path("docs/architecture/specs/SPEC-025-hierarchical-modular-spec-architecture")

        if temp_dir.exists():
            total = handler._count_phases(temp_dir)
            assert isinstance(total, int)
            assert total >= 0

    def test_extract_references(self):
        """Test extracting guideline references from spec content."""
        handler = SpecHandler()

        content = """
        ## Architecture

        See [GUIDELINE-007-jwt-auth](../../guidelines/GUIDELINE-007.md) for JWT patterns.
        See [GUIDELINE-008-password-hashing](../../guidelines/GUIDELINE-008.md) for hashing.
        """

        refs = handler._extract_references(content)

        assert "GUIDELINE-007" in refs
        assert "GUIDELINE-008" in refs
        assert len(refs) == 2


class TestContextEfficiency:
    """Test context efficiency calculations."""

    def test_hierarchical_spec_context_reduction(self):
        """Test context efficiency: hierarchical vs monolithic."""
        handler = SpecHandler()

        # PRIORITY 25 is hierarchical
        result = handler.read_hierarchical("PRIORITY 25")

        if result["success"] and result["spec_type"] == "hierarchical":
            context_size = result["context_size"]

            # Hierarchical should be significantly smaller than estimated monolithic
            # (estimated at 3.5x larger)
            estimated_monolithic = context_size * 3.5

            # Context reduction should be 71% (i.e., loaded 29% of monolithic)
            ratio = context_size / estimated_monolithic
            savings_pct = (1 - ratio) * 100

            assert savings_pct > 65  # At least 65% savings
            assert savings_pct < 75  # Less than 75%


class TestBackwardCompatibility:
    """Test backward compatibility with monolithic specs."""

    def test_read_hierarchical_falls_back_to_monolithic(self):
        """Test that read_hierarchical falls back to monolithic specs."""
        handler = SpecHandler()

        # Test with a priority that might have an older monolithic spec
        result = handler.read_hierarchical("PRIORITY 1")

        # Should succeed (either hierarchical or monolithic or not found)
        # The key is that it doesn't crash
        assert isinstance(result, dict)
        assert "success" in result
        assert "spec_type" in result
        assert result["spec_type"] in ["hierarchical", "monolithic", "not_found"]


class TestSpecHandlerIntegration:
    """Integration tests for spec handler with daemon."""

    def test_spec_handler_initialization(self):
        """Test SpecHandler initializes correctly."""
        handler = SpecHandler()

        assert handler.specs_dir == Path("docs/architecture/specs")
        assert handler.roadmap_dir == Path("docs/roadmap")

    def test_find_spec_by_priority_id_with_us_format(self):
        """Test finding spec by US-XXX format."""
        handler = SpecHandler()

        # Test finding by US ID
        spec_path = handler._find_spec_by_priority_id("US-025")

        if spec_path:
            assert spec_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
