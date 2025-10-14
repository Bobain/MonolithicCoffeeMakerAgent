"""
ACE (Agentic Context Engineering) Framework

Enables continuous agent improvement through execution observation,
reflection, and playbook curation.

Reference: https://www.arxiv.org/abs/2510.04618
"""

from coffee_maker.autonomous.ace.curator import ACECurator
from coffee_maker.autonomous.ace.embeddings import compute_similarity, get_embedding
from coffee_maker.autonomous.ace.models import (
    ConsolidatedInsight,
    DeltaItem,
    Evidence,
    ExecutionTrace,
    ExternalObservation,
    InternalObservation,
    Playbook,
    PlaybookBullet,
)
from coffee_maker.autonomous.ace.playbook_loader import PlaybookLoader
from coffee_maker.autonomous.ace.reflector import ACEReflector

__all__ = [
    "ExecutionTrace",
    "ExternalObservation",
    "InternalObservation",
    "DeltaItem",
    "Evidence",
    "Playbook",
    "PlaybookBullet",
    "ConsolidatedInsight",
    "ACEReflector",
    "ACECurator",
    "PlaybookLoader",
    "get_embedding",
    "compute_similarity",
]
