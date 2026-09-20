# API Reference — Primary Surfaces

Function signatures in the installed package are authoritative. This page documents the intended public contract.

## Factual core

### `LongTermMemory(...)`
Opens a governed local fact store.

### `remember_fact(text, provenance=None, ...)`
Trusted confirmed write.

### `add_inferred_fact(text, provenance=None, ...)`
Attempts inferred admission through the configured gates.

### `correct_fact_version(fact_id, replacement_text, provenance=None, ...)`
Retires one exact version and creates a linked current replacement.

### `forget_fact_version(fact_id=..., text=...)`
`fact_id` is identity-scoped. The compatibility `text=` path retains broader semantic behavior.

### `prohibit_fact_pattern(text)`
Creates a semantic prohibition.

### `read_view()` / `search()` / `answer()` / `refresh()`
Inference and refresh surfaces over governed current state.

## General memory

### `GeneralMemorySystem(core, external_source_resolver=None)`
Creates episodic, semantic, procedural, consolidation, adaptive retrieval, and source-governance layers around a `LongTermMemory` core. `external:` provenance is invalid unless the resolver authorizes it.

### `episodic.remember(..., source_ids, source_policy="all")`
Stores a timestamped source-governed event.

### `semantic.remember(..., source_ids, source_policy="all", merge_sources=False)`
Creates or updates a concept. Existing concept sources are replaced by default; `merge_sources=True` is explicit cumulative provenance.

### `procedural.remember(..., source_ids, source_policy="all")`
Stores a procedure definition.

### `procedural.record_outcome(..., success, source_ids, source_policy="all")`
Stores a source-linked outcome event. Governed reliability uses only currently valid outcomes.

### `recall(query, limit=12, as_of=None)`
Cross-memory retrieval under one refreshed/pinned governance session.

### `integrity()`
Actively refreshes core and sidecars and reports states plus reasons.

## Source policies

`all`: every source must be inference-valid.

`any`: at least one source must be inference-valid. Use only when each source independently supports the whole record.

## Trusted-host warning

No Python method proves that a human approved an operation. Authentication, authorization, model-tool permissions, rate limits, and tenant isolation belong to the host application.
