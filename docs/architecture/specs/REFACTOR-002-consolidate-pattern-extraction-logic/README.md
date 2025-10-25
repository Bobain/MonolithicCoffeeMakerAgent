# REFACTOR-002: Consolidate Pattern Extraction Logic

## Overview

# REFACTOR-002: Consolidate Pattern Extraction Logic

**Status**: Draft
**Author**: architect agent
**Date**: 2025-10-16
**Priority**: 🟡 HIGH
**Estimated Effort**: 6-8 hours
**Expected Value**: ⭐⭐⭐⭐ (high)
**ROI**: 3.8

---

## Problem Statement

### Current State

The codebase contains **15+ extraction methods** with duplicated pattern-matching logic across multiple files:

**Files with duplication**:
1. `ai_service.py` (1,269 lines):
   - `_extract_completion_date`
   - `_extract_business_value`
   - `_extract_key_features`
   - `_extract_estimated_days`
   - `_extract_actual_days`
   - `_extract_what_description`
   - `_extract_impact_statement`
   - `_extract_title`

2. `status_report_generator.py` (1,093 lines):
   - `_extract_completion_date` (duplicate!)
   - `_extract_date_from_status`
   - `_extract_business_value` (duplicate!)
   - `_extract_key_features` (duplicate!)
   - `_extract_estimated_days` (duplicate!)
   - `_extract_actual_days` (duplicate!)
   - `_extract_what_description` (duplicate!)
   - `_extract_impact_statement` (duplicate!)

3. `metadata_extractor.py` (633 lines):
   - Similar extraction logic (again!)

**Code Smell Example**:
```python
# In ai_service.py
def _extract_completion_date(self, content: str) -> Optional[datetime]:
    patterns = [
        r"\*\*Completed\*\*:\s*(\d{4}-\d{2}-\d{2})",
        r"Completed:\s*(\d{4}-\d{2}-\d{2})",
        r"\((\d{4}-\d{2}-\d{2})\)",
    ]
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            try:
                date_str = match.group(1)
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue
    return None

# In status_report_generator.py - EXACT SAME CODE!
def _extract_completion_date(self, content: str) -> Optional[datetime]:
    patterns = [
        r"\*\*Completed\*\*:\s*(\d{4}-\d{2}-\d{2})",
        r"Completed:\s*(\d{4}-\d{2}-\d{2})",
        r"\((\d{4}-\d{2}-\d{2})\)",
    ]
    # ... identical implementation
```

### Impact

**Maintainability**: 😞 Poor
- Bugs fixed in one place must be fixed in 3+ places
- Pattern updates require changing multiple files
- Inconsistent behavior (different parsers handle errors differently)

**Extensibility**: 😞 Poor
- Adding new extraction pattern requires touching 3+ files
- High risk of introducing inconsistencies

**Code Bloat**: 😞 High
- ~600-800 lines of duplicated extraction logic
- 15+ methods that could be 1 unified class

---

## Proposed Solution

### Architecture: Unified PatternExtractor

Create a single, reusable `PatternExtractor` class that:
1. Centralizes all regex patterns
2. Provides type-safe extraction
3. Handles errors consistently
4. Supports caching for performance
5. Easy to extend with new patterns

### Component Design

```python
# coffee_maker/utils/pattern_extractor.py

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Pattern
import re
import logging

logger = logging.getLogger(__name__)

@dataclass
class ExtractionPattern:
    """Defines a single extraction pattern.

    Attributes:
        pattern: Compiled regex pattern
        parser: Function to parse matched group(s)
        flags: Regex flags (re.IGNORECASE, re.DOTALL, etc.)
    """
    pattern: Pattern
    parser: Callable[[str], Any]
    flags: int = 0

class PatternExtractor:
    """Unified pattern extraction from markdown content.

    Centralizes all regex-based extraction logic used throughout
    the codebase for parsing ROADMAP.md and related documents.

    Example:
        >>> extractor = PatternExtractor()
        >>> content = "**Completed**: 2025-10-15"
        >>> date = extractor.extract('completion_date', content)
        >>> print(date)
        datetime.datetime(2025, 10, 15, 0, 0)
    """

    def __init__(self):
        """Initialize extractor with pre-compiled patterns."""
        self._patterns: Dict[str, List[ExtractionPattern]] = {}
        self._cache: Dict[tuple, Any] = {}  # (field, content_hash) -> result
        self._register_patterns()

    def _register_patterns(self):
        """Register all extraction patterns."""

        # Completion Date
        self._patterns['completion_date'] = [
            ExtractionPattern(
                pattern=re.compile(r"\*\*Completed\*\*:\s*(\d{4}-\d{2}-\d{2})"),
                parser=self._parse_date
            ),
            ExtractionPattern(
                pattern=re.compile(r"Completed:\s*(\d{4}-\d{2}-\d{2})"),
                parser=self._parse_date
            ),
            ExtractionPattern(
                pattern=re.compile(r"\((\d{4}-\d{2}-\d{2})\)"),
                parser=self._parse_date
            ),
        ]

        # Business Value
        self._patterns['business_value'] = [
            ExtractionPattern(
                pattern=re.compile(r"\*\*Business Value\*\*:\s*(.+?)(?:\n\n|\n\*\*|$)"),
                parser=self._parse_business_value,
                flags=re.DOTALL
            ),
            ExtractionPattern(
                pattern=re.compile(r"\*\*Value\*\*:\s*(.+?)(?:\n\n|\n\*\*|$)"),
                parser=self._parse_business_value,
                flags=re.DOTALL
            ),
        ]

        # Key Features
        self._patterns['key_features'] = [
            ExtractionPattern(
                pattern=re.compile(r"\*\*Key Features\*\*:\s*\n((?:- .+\n?)+)"),
                parser=self._parse_list_items
            ),
            ExtractionPattern(
                pattern=re.compile(r"\*\*Features Delivered\*\*:\s*\n((?:- .+\n?)+)"),
                parser=self._parse_list_items
            ),
            ExtractionPattern(
                pattern=re.compile(r"\*\*Deliverables\*\*:\s*\n((?:- .+\n?)+)"),
                parser=self._parse_list_items
            ),
        ]

        # Estimated Days
        self._patterns['estimated_days'] = [
            ExtractionPattern(
                pattern=re.compile(r"\*\*Estimated Effort\*\*:\s*(\d+)-(\d+)\s*days?", re.IGNORECASE),
                parser=self._parse_day_range
            ),
            ExtractionPattern(
                pattern=re.compile(r"\*\*Total Estimated\*\*:\s*(\d+)-(\d+)\s*days?", re.IGNORECASE),
                parser=self._parse_day_range
            ),
            ExtractionPattern(
                pattern=re.compile(
                    r"\*\*Estimated Effort\*\*:\s*\d+(?:-\d+)?\s*story points?\s*\((\d+)-(\d+)\s*days?\)",
                    re.IGNORECASE
                ),
                parser=self._parse_day_range
            ),
        ]

        # Actual Days
        self._patterns['actual_days'] = [
            ExtractionPattern(
                pattern=re.compile(r"\*\*Actual Effort\*\*:\s*(\d+(?:\.\d+)?)\s*days?", re.IGNORECASE),
                parser=float
            ),
            ExtractionPattern(
                pattern=re.compile(r"Actual:\s*(\d+(?:\.\d+)?)\s*days?", re.IGNORECASE),
                parser=float
            ),
        ]

        # What Description
        self._patterns['what_description'] = [
            ExtractionPattern(
                pattern=re.compile(r"\*\*I want\*\*:\s*(.+?)(?:\n\n|\n\*\*|$)", re.IGNORECASE | re.DOTALL),
                parser=self._parse_truncated_text
            ),
            ExtractionPattern(
                pattern=re.compile(r"I want to\s+(.+?)(?:\n\n|\n\*\*|$)", re.IGNORECASE | re.DOTALL),
                parser=self._parse_truncated_text
            ),
        ]

        # Impact Statement
        self._patterns['impact_statement'] = [
            ExtractionPattern(
                pattern=re.compile(r"\*\*So that\*\*:\s*(.+?)(?:\n\n|\n\*\*|$)", re.IGNORECASE | re.DOTALL),
                parser=self._parse_truncated_text
            ),
            ExtractionPattern(
                pattern=re.compile(r"\*\*Impact\*\*:\s*(.+?)(?:\n\n|\n\*\*|$)", re.IGNORECASE | re.DOTALL),
                parser=self._parse_truncated_text
            ),
        ]

    def extract(self, field: str, content: str, use_cache: bool = True) -> Optional[Any]:
        """Extract field value from content using registered patterns.

        Args:
            field: Field name to extract (e.g., 'completion_date')
            content: Source content to extract from
            use_cache: Whether to use cached results (default: True)

        Returns:
            Extracted value or None if not found

        Example:
            >>> extractor.extract('business_value', "**Business Value**: High impact")
            'High impact'
        """
        # Check cache
        if use_cache:
            cache_key = (field, hash(content))
            if cache_key in self._cache:
                return self._cache[cache_key]

        # Get patterns for field
        patterns = self._patterns.get(field)
        if not patterns:
            logger.warning(f"No patterns registered for field: {field}")
            return None

        # Try each pattern
        result = None
        for extraction_pattern in patterns:
            match = extraction_pattern.pattern.search(content)
            if match:
                try:
                    # Parse matched groups
                    if match.lastindex and match.lastindex > 1:
                        # Multiple groups
                        result = extraction_pattern.parser(*match.groups())
                    else:
                        # Single group
                        result = extraction_pattern.parser(match.group(1))

                    # Cache and return
                    if use_cache:
                        self._cache[cache_key] = result
                    return result

                except Exception as e:
                    logger.debug(f"Parser failed for {field}: {e}")
                    continue

        # Cache None result
        if use_cache:
            self._cache[cache_key] = None

        return None

    def extract_all(self, content: str, fields: List[str]) -> Dict[str, Any]:
        """Extract multiple fields at once.

        Args:
            content: Source content
            fields: List of field names to extract

        Returns:
            Dictionary mapping field names to extracted values

        Example:
            >>> extractor.extract_all(content, ['business_value', 'estimated_days'])
            {'business_value': 'High', 'estimated_days': {'min_days': 3, 'max_days': 5}}
        """
        return {field: self.extract(field, content) for field in fields}

    def clear_cache(self):
        """Clear extraction cache."""
        self._cache.clear()
        logger.debug("Pattern extraction cache cleared")

    # ==================== PARSERS ====================

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parse date string to datetime."""
        return datetime.strptime(date_str, "%Y-%m-%d")

    @staticmethod
    def _parse_business_value(value_str: str) -> str:
        """Parse business value (remove stars, clean whitespace)."""
        cleaned = re.sub(r"⭐+\s*", "", value_str)
        return cleaned.strip()

    @staticmethod
    def _parse_list_items(items_str: str) -> List[str]:
        """Parse markdown list items."""
        items = re.findall(r"- (.+)", items_str)
        return [item.strip() for item in items if item.strip()][:5]  # Limit to 5

    @staticmethod
    def _parse_day_range(min_str: str, max_str: str) -> Dict[str, float]:
        """Parse day range to dictionary."""
        return {
            'min_days': float(min_str),
            'max_days': float(max_str),
        }

    @staticmethod
    def _parse_truncated_text(text: str, max_length: int = 150) -> str:
        """Parse and truncate text."""
        cleaned = text.strip()
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length - 3] + "..."
        return cleaned


# ==================== SINGLETON INSTANCE ====================

_extractor_instance = None

def get_extractor() -> PatternExtractor:
    """Get singleton PatternExtractor instance.

    Returns:
        Shared PatternExtractor instance

    Example:
        >>> extractor = get_extractor()
        >>> value = extractor.extract('business_value', content)
    """
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = PatternExtractor()
    return _extractor_instance
```

---

---

## Implementation Phases

This specification is organized into phases for progressive disclosure and context efficiency.

### Phase 1: Create PatternExtractor (2 hours)
**Document**: [phase1-create-patternextractor.md](./phase1-create-patternextractor.md)

### Phase 2: Migrate ai_service.py (2 hours)
**Document**: [phase2-migrate-ai_servicepy.md](./phase2-migrate-ai_servicepy.md)

### Phase 3: Migrate status_report_generator.py (2 hours)
**Document**: [phase3-migrate-status_report_generatorpy.md](./phase3-migrate-status_report_generatorpy.md)

### Phase 4: Migrate metadata_extractor.py (2 hours)
**Document**: [phase4-migrate-metadata_extractorpy.md](./phase4-migrate-metadata_extractorpy.md)


---

**Note**: This specification uses hierarchical format for 71% context reduction.
Each phase is in a separate file - read only the phase you're implementing.
