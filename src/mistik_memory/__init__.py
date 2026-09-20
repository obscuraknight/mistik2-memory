"""Local companion memory with separate human-confirmed and inferred writes.

Trusted hosts own authorization. All inference-facing readers filter current
prohibitions; primary snapshots require refresh after another writer changes them.
See README and UPGRADING for parser, durability, audit, and encryption limits.
"""
__version__ = "2.2.0"

from .audit import audit_reply, claim_evidence, claim_is_grounded, detect_memory_claims
from .correction_store import (
    INTEGRITY_DEGRADED,
    INTEGRITY_MISSING,
    INTEGRITY_VALID,
    CorrectionStore,
)
from .gate import (
    gate_fact,
    gate_person,
    set_semantic_similarity_fn,
    tombstone_match_reason,
)
from .doubt import (
    ClarificationLog,
    doubt_score,
    evidence,
    filter_for_prompt,
    questions_for,
    shaky_facts,
)
from .long_memory import LongTermMemory, MemoryDegraded
from .relations import Relation
from .retrieval import Retriever, rank_for_prompt, tokenize
from .storage_context import StorageContext
from .embeddings import hashed_embed_fn, embed_text
from .ingest import ingest_messages, ingest_turn, rewrite_first_person
from .answer import answer, retrieve, token_f1
from .associate import AssociationIndex, associate
from .companion import Companion
from .correct import looks_like_correction, match_facts
from . import locomo
from . import relations

__all__ = [
    "__version__",
    "StorageContext",
    "CorrectionStore",
    "LongTermMemory",
    "MemoryDegraded",
    "relations",
    "Relation",
    "questions_for",
    "shaky_facts",
    "filter_for_prompt",
    "evidence",
    "doubt_score",
    "ClarificationLog",
    "Retriever",
    "rank_for_prompt",
    "gate_fact",
    "gate_person",
    "tombstone_match_reason",
    "set_semantic_similarity_fn",
    "audit_reply",
    "claim_is_grounded",
    "claim_evidence",
    "detect_memory_claims",
    "hashed_embed_fn",
    "embed_text",
    "ingest_messages",
    "ingest_turn",
    "rewrite_first_person",
    "answer",
    "retrieve",
    "token_f1",
    "associate",
    "AssociationIndex",
    "Companion",
    "looks_like_correction",
    "match_facts",
    "locomo",
    "INTEGRITY_MISSING",
    "INTEGRITY_VALID",
    "INTEGRITY_DEGRADED",
    "GeneralMemorySystem",
    "AdaptiveRetriever",
    "EpisodicMemory",
    "SemanticMemory",
    "ProceduralMemory",
    "Consolidator",
    "salience_score",
]

from .general_memory import GeneralMemorySystem, AdaptiveRetriever
from .episodic import EpisodicMemory
from .semantic import SemanticMemory
from .procedural import ProceduralMemory
from .salience import salience_score
from .consolidation import Consolidator
