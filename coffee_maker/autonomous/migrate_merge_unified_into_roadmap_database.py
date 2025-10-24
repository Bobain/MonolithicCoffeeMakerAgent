#!/usr/bin/env python3
"""Migration: Merge UnifiedDatabase into RoadmapDatabase.

This migration consolidates two classes that manage the same database:
- UnifiedDatabase (generic name, confusing)
- RoadmapDatabase (specific name, clear purpose)

Both classes access data/roadmap.db, so having two classes is redundant and confusing.

Strategy:
1. Copy useful methods from UnifiedDatabase to RoadmapDatabase
2. Update all imports from UnifiedDatabase → RoadmapDatabase
3. Delete unified_database.py
4. Test that all functionality works

Methods to merge:
- get_items_with_specs() → RoadmapDatabase
- get_items_needing_specs() → RoadmapDatabase
- get_database_stats() → RoadmapDatabase
- link_spec_to_roadmap() → RoadmapDatabase (if not already there)
- get_next_implementation_task() → RoadmapDatabase

Author: architect
Date: 2025-10-24
Related: User feedback on avoiding generic naming
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("=" * 70)
logger.info("MIGRATION PLAN: UnifiedDatabase → RoadmapDatabase")
logger.info("=" * 70)
logger.info("")
logger.info("Files to update:")
logger.info("  1. coffee_maker/autonomous/roadmap_database.py")
logger.info("     - Add methods from UnifiedDatabase")
logger.info("")
logger.info("  2. coffee_maker/autonomous/dump_technical_spec.py")
logger.info("     - Change: from unified_database import → from roadmap_database import")
logger.info("")
logger.info("  3. coffee_maker/autonomous/daemon.py")
logger.info("     - Change: get_unified_database() → RoadmapDatabase()")
logger.info("")
logger.info("  4. .claude/skills/shared/code_review_tracking/review_tracking_skill.py")
logger.info("     - Change: get_unified_database() → RoadmapDatabase()")
logger.info("")
logger.info("  5. .claude/skills/shared/technical_spec_database/unified_spec_skill.py")
logger.info("     - Change: get_unified_database() → RoadmapDatabase()")
logger.info("")
logger.info("  6. coffee_maker/autonomous/unified_database.py")
logger.info("     - DELETE this file (functionality merged into RoadmapDatabase)")
logger.info("")
logger.info("Benefits:")
logger.info("  ✅ Single class for data/roadmap.db")
logger.info("  ✅ Clear naming: RoadmapDatabase (not generic)")
logger.info("  ✅ Less confusion about which class to use")
logger.info("  ✅ Easier to maintain")
logger.info("")
logger.info("This is a MANUAL migration - requires careful code updates")
logger.info("Run tests after each change!")
