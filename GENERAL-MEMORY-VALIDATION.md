# General Memory Validation — 2.2.0

The general-memory layer is validated as a governed derivative of the factual core, not as an independent authority.

## Invariants under test

- every derived write declares typed sources;
- external sources require a host resolver;
- one inference operation uses one refreshed core identity set and one pinned generation of each derived store;
- forgotten, tombstoned, superseded, missing, legacy-unattributed, or cyclic sources fail closed;
- `source_policy="all"` requires every source;
- `source_policy="any"` survives revocation of one independently sufficient source until all alternatives are invalid;
- semantic updates replace stale provenance by default;
- procedure outcome reliability is computed only from currently valid source-linked outcomes;
- same-text reconfirmation under a new fact ID does not resurrect descendants tied to an old forgotten ID;
- external resolver revocation is observed on the next inference operation;
- malformed sidecars do not become empty trusted memory.

## Snapshot semantics

General-memory reads refresh the factual core and pin the derived stores at the start of the inference session. A concurrent commit after that point is intentionally observed on the next inference operation, not halfway through the current one.

## Legacy state

Legacy source-free records remain auditable but are inference-ineligible. Legacy procedure aggregate outcome counters remain available for audit/backward compatibility; governed reliability is based on source-linked 2.2 outcome events.

## Limitations

The source graph is a governance graph, not a general theorem prover. The host decides whether `any` or `all` accurately represents the logical support relationship. External resolver truth is also a host responsibility.
