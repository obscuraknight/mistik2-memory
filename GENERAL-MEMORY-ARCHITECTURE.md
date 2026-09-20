# General Memory Architecture — 2.2

Mistik2 Memory 2.2 keeps the governed factual core authoritative and makes higher-order memory explicitly dependent on source governance.

## Invariants

1. Every derived write declares one or more typed sources.
2. External sources are invalid unless the host explicitly resolves them as valid.
3. Every inference-facing operation refreshes the core and pins one validated generation of each derived store.
4. Transitive provenance resolution uses the pinned session state; it does not re-read sidecars mid-query.
5. A source policy is explicit: `all` means conjunctive evidence, `any` means independently sufficient evidence.
6. Cyclic provenance fails closed.
7. Invalid derived records remain auditable on disk but are excluded from inference.
8. Procedure outcome evidence is source-linked; invalidated outcome evidence stops affecting governed reliability.

## Typed references

- `fact:<fact_id>`
- `episode:<episode_id>`
- `semantic:<semantic_id>`
- `procedure:<procedure_id>`
- `external:<host-id>`

Source references reject control characters and pathological identifier sizes.

## Snapshot model

A `SourceGovernance.read_session()` performs a core refresh, obtains the active/forgotten fact identities, and snapshots the registered episodic, semantic, and procedural records. All layers inside that operation resolve provenance against the same pinned generation.

This is read consistency for one inference operation, not a global transaction across all files. A writer that commits after the snapshot becomes visible on the next inference operation.

## Source policies

`source_policy="all"` is the conservative default. Every declared source must remain inference-valid.

`source_policy="any"` is for records where each source independently supports the whole derived record. Developers should not use `any` when the derived statement logically depends on combining several pieces of evidence.

## External sources

An external source has no built-in truth authority. It becomes inference-valid only if `external_source_resolver(source_id)` returns truthy for the current operation. Resolver errors fail closed for expected lookup/runtime/data errors.

## Semantic updates

Updating a semantic concept replaces its source set by default, preventing a new summary from being accidentally authorized by stale evidence from an earlier version. `merge_sources=True` is an explicit opt-in for intentionally cumulative provenance.

## Procedure outcomes

Procedure definition provenance and outcome provenance are separate. Each outcome stores its own sources and source policy. The public aggregate counters are retained for audit/backward compatibility, but inference-facing reliability is calculated from currently valid outcome events.

Legacy procedures that only contain aggregate counters have neutral governed reliability until new source-linked outcomes are recorded.

## Legacy migration

2.0/2.1 sidecars remain readable. Missing `source_policy` is interpreted as `all`. Source-free legacy records remain auditable but are not inference-valid. The library does not invent provenance during migration.
