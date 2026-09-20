# Upgrading Mistik2 Memory

## 2.2.0

2.2 tightens production governance and can change behavior for integrations that used implicit external trust.

### External sources now require a resolver

`external:<id>` no longer authorizes a governed derived write by itself.

```python
memory = GeneralMemorySystem(
    core,
    external_source_resolver=lambda source_id: source_id in trusted_external_ids,
)
```

If no resolver is supplied, external sources fail closed.

### Derived reads use pinned sidecar snapshots

A single inference operation now uses one refreshed core identity snapshot and one pinned generation of every derived store. Code should not depend on a sidecar change becoming visible halfway through one recall operation.

### Source policy

Derived writes accept `source_policy="all"` (default) or `source_policy="any"`. Use `any` only when each source independently supports the complete derived record.

### Semantic updates replace sources by default

Updating an existing semantic concept replaces its source set. Use `merge_sources=True` only when cumulative provenance is intentional.

### Procedure outcomes are provenance-bearing events

`record_outcome()` still requires `source_ids`, but those sources are now stored on the outcome event rather than merged into the procedure definition's source set. Governed reliability ignores outcomes whose sources later become invalid.

### Episodic timestamps are normalized

`occurred_at` and `as_of` must be valid ISO-8601 timestamps. Naive timestamps are interpreted as UTC; offset-aware timestamps are normalized before comparison.

### Health reporting refreshes state

`GeneralMemorySystem.integrity()` actively refreshes the core and cognitive sidecars and returns a `reasons` map alongside state labels.

## 2.1.0

Derived-memory writes became source-governed. Every episode, semantic concept, procedure, and procedure outcome must declare typed sources. Direct cognitive-layer construction requires governance unless explicitly created with `allow_ungoverned=True`. Source-free legacy records remain auditable but are suppressed from inference.

## 1.7.0

Exact identity forgetting was separated from semantic prohibition. `forget_fact_version(fact_id=...)` targets only that fact generation. Use `prohibit_fact_pattern()` when the intent is a broader concept/pattern ban.

## Older releases

Read the changelog before crossing older major behavior changes. Existing stores are not automatically rewritten merely because the package is upgraded; migrations are validation-driven and intentionally conservative.
