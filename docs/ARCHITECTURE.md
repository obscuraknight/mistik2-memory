# Architecture

Mistik2 Memory is a local, file-backed governed-memory engine. The factual core is the authority for current fact identity; episodic, semantic, and procedural stores are derived systems whose inference eligibility depends on explicit provenance.

## Governed factual core

`LongTermMemory` stores confirmed and inferred facts with stable identities, provenance, correction/supersession history, exact identity forgetting, and semantic prohibitions.

Current reads exclude retired, superseded, corrected, tombstoned, and exactly forgotten identities. Corrupt governed state fails closed.

## Derived stores

`GeneralMemorySystem` adds episodic, semantic, and procedural stores. Every derived write declares typed sources and a source policy.

One inference session pins:

1. refreshed active/forgotten fact IDs from the core;
2. one validated generation of the episodic store;
3. one validated generation of the semantic store;
4. one validated generation of the procedural store.

Transitive provenance resolution uses only that pinned session state. This prevents a single recall from mixing multiple sidecar generations.

## Source semantics

`source_policy="all"` means every source is required. `source_policy="any"` means each source independently supports the complete derived record and any one valid source is sufficient.

`external:` references are not automatically trusted. A host resolver must attest them for each inference operation.

## Semantic memory updates

Updating an existing semantic concept replaces its source set by default. This prevents a new summary from being accidentally authorized by stale evidence left over from an older version. Cumulative provenance requires `merge_sources=True`.

## Procedural memory

Procedure definition provenance is separate from outcome provenance. Outcomes are persisted as source-linked events. Reliability exposed to inference is computed from currently valid outcomes; historical aggregate counters remain audit metadata and backward-compatible state.

## Persistence

Writes use same-directory temporary files, owner-only permissions, file fsync, atomic replacement, and parent-directory sync where supported. Stable lock files coordinate cooperating writers; POSIX lock opening refuses symlink traversal and non-regular lock targets.

The core uses recovery journals/receipts for logical operations that span primary memory, correction state, and archive state. The architecture is recovery-oriented rather than distributed ACID.

## Read consistency

Core fact reads within one general-memory inference operation observe the refreshed in-memory core generation. Derived records are pinned for the same inference session. A concurrent commit after that snapshot is visible on the next inference operation.

## Security boundary

Trusted-host APIs are capabilities, not authentication. The host owns user authentication, authorization, tenant isolation, quotas, model-tool permissions, backup policy, and encryption-secret management.

See `SECURITY.md` and `DURABILITY.md` for non-guarantees.
