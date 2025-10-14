"""ACE Curator - Consolidates deltas into agent playbooks.

The Curator is the third component of the ACE framework. It:
1. Loads delta items from Reflector
2. Uses semantic similarity to de-duplicate insights
3. Merges similar deltas into existing bullets or adds new ones
4. Prunes low-value bullets to keep playbook focused
5. Tracks health metrics

De-duplication: Uses OpenAI embeddings with cosine similarity > 0.85 threshold
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from coffee_maker.autonomous.ace.config import ACEConfig, get_default_config
from coffee_maker.autonomous.ace.embeddings import compute_similarity, get_embedding
from coffee_maker.autonomous.ace.models import (
    DeltaItem,
    HealthMetrics,
    Playbook,
    PlaybookBullet,
)
from coffee_maker.autonomous.ace.playbook_loader import PlaybookLoader
from coffee_maker.utils.file_io import write_json_file

logger = logging.getLogger(__name__)


class ACECurator:
    """Consolidate delta items into agent playbooks."""

    def __init__(self, agent_name: str, config: Optional[ACEConfig] = None):
        """Initialize curator.

        Args:
            agent_name: Name of the agent (e.g., "code_developer")
            config: ACE configuration (optional)
        """
        self.agent_name = agent_name
        self.config = config or get_default_config()
        self.playbook_loader = PlaybookLoader(agent_name, config)

        # Statistics for this session
        self.bullets_added = 0
        self.bullets_updated = 0
        self.bullets_pruned = 0
        self.deltas_processed = 0

    def consolidate_deltas(self, delta_files: Optional[List[Path]] = None) -> Playbook:
        """Main entry point - consolidate deltas into playbook.

        Args:
            delta_files: List of delta file paths (optional, auto-discovers if None)

        Returns:
            Updated Playbook

        Example:
            >>> curator = ACECurator("code_developer")
            >>> playbook = curator.consolidate_deltas()
            >>> print(f"Added {curator.bullets_added} new bullets")
        """
        logger.info(f"Starting consolidation for {self.agent_name}")

        # Load delta files
        if delta_files is None:
            delta_files = self._discover_delta_files()
        deltas = self._load_deltas(delta_files)
        logger.info(f"Loaded {len(deltas)} delta items from {len(delta_files)} files")

        # Load existing playbook
        playbook = self._load_playbook()
        logger.info(f"Loaded playbook with {playbook.total_bullets} bullets")

        # Process each delta
        for delta in deltas:
            self._process_delta(delta, playbook)
            self.deltas_processed += 1

        # Prune low-value bullets
        self._prune_low_value_bullets(playbook)

        # Update health metrics
        self._update_health_metrics(playbook)

        # Update playbook metadata
        playbook.total_bullets = sum(len(bullets) for bullets in playbook.categories.values())
        playbook.last_updated = datetime.now()

        # Save playbook
        self.playbook_loader.save(playbook)
        logger.info(f"Saved playbook with {playbook.total_bullets} bullets")

        # Save curation report
        self._save_curation_report(playbook)

        logger.info(
            f"Consolidation complete: {self.bullets_added} added, "
            f"{self.bullets_updated} updated, {self.bullets_pruned} pruned"
        )

        return playbook

    def _discover_delta_files(self) -> List[Path]:
        """Discover all delta files in delta directory.

        Returns:
            List of delta file paths
        """
        delta_dir = self.config.delta_dir / self.agent_name
        if not delta_dir.exists():
            logger.warning(f"Delta directory not found: {delta_dir}")
            return []

        delta_files = list(delta_dir.glob("delta_*.json"))
        logger.info(f"Discovered {len(delta_files)} delta files in {delta_dir}")
        return delta_files

    def _load_deltas(self, delta_files: List[Path]) -> List[DeltaItem]:
        """Load delta items from files.

        Args:
            delta_files: List of delta file paths

        Returns:
            List of DeltaItem objects
        """
        deltas = []
        for path in delta_files:
            try:
                with open(path, "r") as f:
                    data = json.load(f)

                # Handle both single delta and list of deltas
                if isinstance(data, list):
                    deltas.extend([DeltaItem.from_dict(d) for d in data])
                else:
                    deltas.append(DeltaItem.from_dict(data))

            except Exception as e:
                logger.error(f"Failed to load delta from {path}: {e}")
                continue

        return deltas

    def _load_playbook(self) -> Playbook:
        """Load existing playbook or create default.

        Returns:
            Playbook instance
        """
        return self.playbook_loader.load()

    def _process_delta(self, delta: DeltaItem, playbook: Playbook):
        """Process single delta (merge or add).

        Args:
            delta: Delta item to process
            playbook: Playbook to update
        """
        # Find similar bullet using semantic similarity
        match = self._find_similar_bullet(delta, playbook, self.config.similarity_threshold)

        if match:
            bullet, similarity = match
            logger.info(f"Found similar bullet {bullet.bullet_id} (similarity: {similarity:.3f})")
            self._merge_bullet(bullet, delta)
            self.bullets_updated += 1
        else:
            logger.info(f"No similar bullet found, adding new: {delta.title}")
            self._add_new_bullet(delta, playbook)
            self.bullets_added += 1

    def _find_similar_bullet(
        self, delta: DeltaItem, playbook: Playbook, threshold: float = 0.85
    ) -> Optional[Tuple[PlaybookBullet, float]]:
        """Find most similar bullet using cosine similarity.

        Args:
            delta: Delta item to match
            playbook: Playbook to search
            threshold: Minimum similarity threshold (default: 0.85)

        Returns:
            (bullet, similarity) if similarity > threshold, else None
        """
        # Get delta embedding
        delta_text = f"{delta.title}: {delta.description}"
        delta_emb = get_embedding(delta_text)

        best_match = None
        best_similarity = threshold

        # Search all bullets in same category
        category = delta.insight_type
        if category in playbook.categories:
            for bullet in playbook.categories[category]:
                if bullet.deprecated:
                    continue

                # Get or compute bullet embedding
                if bullet.embedding is None:
                    bullet.embedding = get_embedding(bullet.content)

                # Compute similarity
                similarity = compute_similarity(delta_emb, bullet.embedding)

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = bullet

        if best_match:
            return (best_match, best_similarity)
        return None

    def _merge_bullet(self, bullet: PlaybookBullet, delta: DeltaItem):
        """Merge delta into existing bullet.

        Updates:
        - helpful_count (increments)
        - confidence (weighted average)
        - priority (takes max)
        - evidence_sources (appends)
        - last_updated (current time)

        Args:
            bullet: Existing bullet to update
            delta: Delta item to merge in
        """
        # Increment helpful count (evidence of usefulness)
        bullet.helpful_count += 1

        # Update confidence (weighted average)
        total_weight = bullet.helpful_count + bullet.harmful_count
        if total_weight > 0:
            bullet.confidence = (bullet.confidence * (total_weight - 1) + delta.confidence) / total_weight

        # Update priority (take higher priority)
        bullet.priority = max(bullet.priority, delta.priority)

        # Add evidence sources
        for evidence in delta.evidence:
            if evidence.trace_id not in bullet.evidence_sources:
                bullet.evidence_sources.append(evidence.trace_id)

        # Update timestamp
        bullet.last_updated = datetime.now()

        logger.debug(
            f"Merged delta {delta.delta_id} into bullet {bullet.bullet_id} "
            f"(helpful: {bullet.helpful_count}, confidence: {bullet.confidence:.2f})"
        )

    def _add_new_bullet(self, delta: DeltaItem, playbook: Playbook):
        """Add new bullet from delta.

        Args:
            delta: Delta item to convert to bullet
            playbook: Playbook to add to
        """
        # Generate embedding
        recommendation_emb = get_embedding(delta.recommendation)

        bullet = PlaybookBullet(
            bullet_id=f"bullet_{int(datetime.now().timestamp() * 1000)}",
            type=delta.insight_type,
            content=delta.recommendation,
            helpful_count=1,  # Start with 1 (this delta is evidence)
            harmful_count=0,
            confidence=delta.confidence,
            priority=delta.priority,
            created_at=datetime.now(),
            last_updated=datetime.now(),
            evidence_sources=[e.trace_id for e in delta.evidence],
            applicability=delta.applicability,
            tags=[],
            embedding=recommendation_emb,
            deprecated=False,
        )

        # Add to appropriate category
        category = delta.insight_type
        if category not in playbook.categories:
            playbook.categories[category] = []
        playbook.categories[category].append(bullet)

        logger.debug(f"Added new bullet {bullet.bullet_id} to category {category}")

    def _prune_low_value_bullets(self, playbook: Playbook):
        """Remove low-value bullets to keep playbook focused.

        Pruning criteria:
        - Low helpful_count (< min_helpful_count)
        - Low effectiveness ratio (helpful / (helpful + harmful))
        - Playbook exceeds max_bullets

        Args:
            playbook: Playbook to prune
        """
        all_bullets = []
        for category, bullets in playbook.categories.items():
            for bullet in bullets:
                if not bullet.deprecated:
                    all_bullets.append((category, bullet))

        # Calculate effectiveness for each bullet
        bullets_with_score = []
        for category, bullet in all_bullets:
            total_count = bullet.helpful_count + bullet.harmful_count
            if total_count > 0:
                effectiveness = bullet.helpful_count / total_count
            else:
                effectiveness = 0.5  # Neutral if no data

            score = effectiveness * bullet.confidence * bullet.priority
            bullets_with_score.append((category, bullet, score))

        # Sort by score (lowest first - candidates for pruning)
        bullets_with_score.sort(key=lambda x: x[2])

        # First pass: Prune bullets with low helpful_count (always prune these)
        pruned = 0
        for category, bullet, score in bullets_with_score:
            # Prune if below min_helpful_count
            if bullet.helpful_count < self.config.min_helpful_count:
                bullet.deprecated = True
                bullet.deprecation_reason = f"Low helpful count: {bullet.helpful_count}"
                pruned += 1
                logger.debug(f"Pruned bullet {bullet.bullet_id}: {bullet.deprecation_reason}")

        # Second pass: Additional pruning if we're still over max_bullets
        total_active = len([b for _, b in all_bullets if not b.deprecated])
        if total_active > self.config.max_bullets:
            to_prune = int((total_active - self.config.max_bullets) * (1 + self.config.pruning_rate))

            for category, bullet, score in bullets_with_score[:to_prune]:
                if not bullet.deprecated:
                    bullet.deprecated = True
                    bullet.deprecation_reason = f"Low effectiveness score: {score:.3f}"
                    pruned += 1
                    logger.debug(f"Pruned bullet {bullet.bullet_id}: {bullet.deprecation_reason}")

        self.bullets_pruned = pruned
        if pruned > 0:
            logger.info(f"Pruned {pruned} low-value bullets")

    def _update_health_metrics(self, playbook: Playbook):
        """Update playbook health metrics.

        Computes:
        - total_bullets (active only)
        - avg_helpful_count
        - effectiveness_ratio (helpful / (helpful + harmful))
        - coverage_score (categories with bullets / total categories)
        - session stats

        Args:
            playbook: Playbook to update metrics for
        """
        all_bullets = []
        for bullets in playbook.categories.values():
            all_bullets.extend([b for b in bullets if not b.deprecated])

        if not all_bullets:
            playbook.health_metrics = HealthMetrics()
            return

        # Total bullets
        total_bullets = len(all_bullets)

        # Average helpful count
        avg_helpful = sum(b.helpful_count for b in all_bullets) / total_bullets

        # Effectiveness ratio
        total_helpful = sum(b.helpful_count for b in all_bullets)
        total_harmful = sum(b.harmful_count for b in all_bullets)
        total_interactions = total_helpful + total_harmful
        if total_interactions > 0:
            effectiveness = total_helpful / total_interactions
        else:
            effectiveness = 0.0

        # Coverage score (categories with bullets)
        categories_with_bullets = len([cat for cat, bullets in playbook.categories.items() if bullets])
        # Assume 10 standard categories
        expected_categories = 10
        coverage = min(1.0, categories_with_bullets / expected_categories)

        playbook.health_metrics = HealthMetrics(
            total_bullets=total_bullets,
            avg_helpful_count=avg_helpful,
            effectiveness_ratio=effectiveness,
            bullets_added_this_session=self.bullets_added,
            bullets_updated_this_session=self.bullets_updated,
            bullets_pruned_this_session=self.bullets_pruned,
            coverage_score=coverage,
        )

        # Update playbook-level effectiveness score
        playbook.effectiveness_score = effectiveness

        logger.info(
            f"Health metrics: {total_bullets} bullets, "
            f"{avg_helpful:.2f} avg helpful, "
            f"{effectiveness:.2%} effectiveness, "
            f"{coverage:.2%} coverage"
        )

    def _save_curation_report(self, playbook: Playbook):
        """Save curation report for this session.

        Args:
            playbook: Updated playbook
        """
        report_dir = self.config.playbook_dir / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = report_dir / f"curation_report_{self.agent_name}_{timestamp}.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": self.agent_name,
            "deltas_processed": self.deltas_processed,
            "bullets_added": self.bullets_added,
            "bullets_updated": self.bullets_updated,
            "bullets_pruned": self.bullets_pruned,
            "playbook_total_bullets": playbook.total_bullets,
            "playbook_effectiveness": playbook.effectiveness_score,
            "health_metrics": (playbook.health_metrics.to_dict() if playbook.health_metrics else None),
        }

        write_json_file(report_path, report)
        logger.info(f"Saved curation report to {report_path}")
