from __future__ import annotations

import contextlib
import copy
import threading
from dataclasses import dataclass

_ALLOWED_KINDS = {"fact", "episode", "semantic", "procedure", "external"}
_STORED_ONLY_KINDS = {"legacy"}


def normalize_source_ids(source_ids, *, required=True, allow_legacy=False):
    if source_ids is None:
        source_ids = []
    if not isinstance(source_ids, (list, tuple, set)):
        raise ValueError("source_ids must be a sequence of typed source references")
    out = []
    seen = set()
    for raw in source_ids:
        if not isinstance(raw, str) or ":" not in raw:
            raise ValueError("source references must use '<kind>:<id>'")
        if len(raw.encode("utf-8")) > 2048 or any(ord(ch) < 32 for ch in raw):
            raise ValueError("source reference is too large or contains control characters")
        kind, ident = raw.split(":", 1)
        kind, ident = kind.strip().lower(), ident.strip()
        if kind not in (_ALLOWED_KINDS | (_STORED_ONLY_KINDS if allow_legacy else set())) or not ident:
            raise ValueError(f"invalid source reference: {raw!r}")
        ref = f"{kind}:{ident}"
        if ref not in seen:
            seen.add(ref)
            out.append(ref)
    if required and not out:
        raise ValueError("derived memory requires at least one declared source")
    return out


@dataclass(frozen=True)
class GovernanceSnapshot:
    available: bool
    forgotten_fact_ids: frozenset[str]
    active_fact_ids: frozenset[str]
    derived_records: dict[str, dict[str, dict]]
    reason: str | None = None

    def records_for(self, kind):
        records = self.derived_records.get(kind, {})
        return [copy.deepcopy(record) for record in records.values()]


class SourceGovernance:
    """One refreshed core-governance snapshot shared by derived reads.

    Outside a read_session(), every inference-facing read refreshes the core.
    Inside a session, all memory layers use exactly the same snapshot.
    """

    def __init__(self, core, *, external_source_resolver=None):
        self.core = core
        self._stores = {}
        self._local = threading.local()
        self._external_source_resolver = external_source_resolver

    def register(self, kind, memory_layer):
        if kind not in {"episode", "semantic", "procedure"}:
            raise ValueError("unsupported governed memory kind")
        self._stores[kind] = memory_layer

    def _fresh_snapshot(self):
        if not self.core.refresh():
            return GovernanceSnapshot(False, frozenset(), frozenset(), {}, "core refresh failed")
        view = self.core.read_view()
        if view.get("degraded"):
            return GovernanceSnapshot(False, frozenset(), frozenset(), {}, view.get("reason") or "core unavailable")
        forgotten = frozenset(self.core.forgotten_fact_ids())
        active = frozenset(f["fact_id"] for f in view.get("facts", []))
        derived = {}
        for kind, layer in self._stores.items():
            records = layer.store.records()
            if layer.store.integrity == "DEGRADED":
                return GovernanceSnapshot(False, forgotten, active, {}, f"{kind} store unavailable: {layer.store.integrity_reason or 'degraded'}")
            derived[kind] = {record["id"]: record for record in records}
        return GovernanceSnapshot(True, forgotten, active, derived, None)

    @contextlib.contextmanager
    def read_session(self):
        depth = getattr(self._local, "depth", 0)
        if depth == 0:
            self._local.snapshot = self._fresh_snapshot()
            self._local.memo = {}
        self._local.depth = depth + 1
        try:
            yield self._local.snapshot
        finally:
            self._local.depth -= 1
            if self._local.depth == 0:
                self._local.snapshot = None
                self._local.memo = None

    def snapshot(self):
        snap = getattr(self._local, "snapshot", None)
        if snap is not None:
            return snap
        return self._fresh_snapshot()

    def _record_for(self, kind, ident, snapshot):
        return snapshot.derived_records.get(kind, {}).get(ident)

    def sources_allowed(self, source_ids, *, snapshot=None, trail=None, policy="all"):
        refs = normalize_source_ids(source_ids, required=True, allow_legacy=True)
        snap = snapshot or self.snapshot()
        if not snap.available:
            return False
        trail = set(trail or ())
        memo = getattr(self._local, "memo", None)
        if policy not in {"all", "any"}:
            return False
        results = []
        for ref in refs:
            if memo is not None and ref in memo:
                results.append(bool(memo[ref]))
                continue
            kind, ident = ref.split(":", 1)
            if kind == "external":
                resolver = self._external_source_resolver
                if resolver is None:
                    allowed = False
                else:
                    try:
                        allowed = bool(resolver(ident))
                    except (LookupError, OSError, RuntimeError, TypeError, ValueError):
                        allowed = False
            elif kind == "legacy":
                allowed = False
            elif kind == "fact":
                allowed = ident not in snap.forgotten_fact_ids and ident in snap.active_fact_ids
            else:
                if ref in trail:
                    allowed = False
                else:
                    record = self._record_for(kind, ident, snap)
                    nested_policy = record.get("source_policy", "all") if record else "all"
                    allowed = bool(record) and self.sources_allowed(
                        record.get("source_ids", []), snapshot=snap, trail=trail | {ref}, policy=nested_policy)
            if memo is not None:
                memo[ref] = bool(allowed)
            results.append(bool(allowed))
        return all(results) if policy == "all" else any(results)

    def validate_write_sources(self, source_ids, *, policy="all"):
        refs = normalize_source_ids(source_ids, required=True)
        if policy not in {"all", "any"}:
            raise ValueError("source_policy must be 'all' or 'any'")
        with self.read_session() as snap:
            if not snap.available:
                raise RuntimeError(snap.reason or "core governance unavailable")
            if not self.sources_allowed(refs, snapshot=snap, policy=policy):
                raise ValueError("one or more declared sources are not currently inference-valid")
        return refs
