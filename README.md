# Mistik2 Memory

**Governed long-term memory for AI systems.**

Mistik2 Memory is a local Python memory engine for agents, assistants, research tools, and private AI applications. It treats memory as governed state rather than a bag of retrieved text: facts have identity, provenance, trust class, history, correction semantics, forgetting semantics, and recovery rules.

**Current release:** 2.2.0 · **Author:** panosk · **License:** Apache-2.0 · **Python:** 3.10+

> Distribution: `mistik2-memory` · Import: `mistik_memory`

## Why this exists

Most AI memory layers optimize retrieval. Mistik2 Memory additionally asks:

- Is this memory confirmed or inferred?
- What source authorizes it?
- Is that source still valid now?
- Was this fact corrected, superseded, or forgotten?
- Can a derived memory outlive the evidence it came from?
- What happens if two processes write at once or a multi-file update is interrupted?

The core is conservative by design: unavailable or corrupt governed state fails closed for inference.

## Memory systems

- **Factual** — confirmed/inferred facts, provenance, supersession, correction history, exact forgetting, semantic prohibition.
- **Episodic** — timestamped events with participants, tags, salience, and typed sources.
- **Semantic** — concepts/abstractions backed by explicit source references.
- **Procedural** — procedures plus source-linked outcome evidence and governed reliability.
- **Consolidation** — creates evidence-linked topic concepts; it does not fabricate source-free facts.
- **Adaptive retrieval** — ranks across memory types without changing trust class.

## The 2.2 governance contract

Every derived write must declare typed sources:

```text
fact:<fact_id>
episode:<episode_id>
semantic:<semantic_id>
procedure:<procedure_id>
external:<host_source_id>
```

Every inference-facing read begins from a refreshed governed core snapshot and pins one validated generation of each derived store for that read. Transitive provenance resolution uses those pinned snapshots; it does not re-read sidecars halfway through the same inference operation.

Derived records support explicit source semantics:

- `source_policy="all"` — every source is required.
- `source_policy="any"` — any one independently sufficient source may authorize the record.

External sources are **denied by default**. A host must provide an `external_source_resolver` that decides whether a named external source is currently valid.

```python
from mistik_memory import GeneralMemorySystem, LongTermMemory

core = LongTermMemory("memory.json", inferred_cap=-1)

def external_source_is_valid(source_id: str) -> bool:
    return source_id in {"calendar:evt-42", "sensor:17"}

memory = GeneralMemorySystem(
    core,
    external_source_resolver=external_source_is_valid,
)
```

## Quick start

```python
from mistik_memory import GeneralMemorySystem, LongTermMemory

core = LongTermMemory("memory.json", inferred_cap=-1)
core.remember_fact(
    "The user lives in Berlin.",
    provenance={"source_message_id": "msg-42"},
)

fact = core.read_view()["facts"][0]

memory = GeneralMemorySystem(core)
episode_id = memory.episodic.remember(
    "The Berlin relocation was completed.",
    tags=["relocation"],
    source_ids=[f"fact:{fact['fact_id']}"],
)

concept_id = memory.semantic.remember(
    "Berlin relocation",
    "The relocation is represented by a governed episode.",
    source_ids=[f"episode:{episode_id}"],
)

procedure_id = memory.procedural.remember(
    "Update address after relocation",
    ["verify address", "update account", "confirm completion"],
    source_ids=[f"semantic:{concept_id}"],
)

print(memory.recall("Berlin relocation", limit=10))
```

If the root fact is later forgotten, tombstoned, superseded, or otherwise no longer active, dependent memories are suppressed from inference transitively. They remain on disk for audit unless explicitly deleted.

## Corrections and forgetting are different operations

```python
# Correct one exact persisted fact while retaining history.
core.correct_fact_version(
    fact_id,
    "Corrected evidence text.",
    provenance={"source_component": "reviewed_import"},
)

# Forget exactly one fact generation.
core.forget_fact_version(fact_id)

# Intentionally create a broader semantic prohibition.
core.prohibit_fact_pattern("The user lives in Paris.")
```

Exact forgetting does not silently become a concept-wide ban. Semantic prohibition is deliberately broader and is a separate API.

## Procedural outcome governance

Procedure definitions and procedure outcomes have separate provenance. Outcome evidence is stored as source-linked events. Reliability used for inference is computed from **currently valid outcome sources**, not only from irreversible aggregate counters.

```python
procedure_id = memory.procedural.remember(
    "Restart local service",
    ["stop service", "start service", "verify health"],
    source_ids=[f"fact:{runbook_fact_id}"],
)

memory.procedural.record_outcome(
    procedure_id,
    success=True,
    source_ids=[f"fact:{incident_result_fact_id}"],
)
```

If the incident result is later forgotten, that outcome stops influencing governed reliability.

## Integrity and health

```python
status = memory.integrity()
print(status)
```

`GeneralMemorySystem.integrity()` actively refreshes the core and all cognitive sidecars before reporting. Do not treat a cached object property as a production health check.

## Persistence model

- Atomic same-directory file replacement.
- Owner-only store/temp/lock permissions where supported.
- Stable per-store locks with symlink-resistant lock-file opening on POSIX.
- Reload-before-mutate for cooperating writers.
- Recovery journals/receipts for core multi-file transitions.
- Parent-directory sync after JSON replacement where the platform supports it.
- Corrupt governed state fails closed instead of becoming an empty “new” memory.

This is a recovery-oriented local storage engine, **not a distributed ACID database**. Read [DURABILITY.md](DURABILITY.md) before production deployment.

## Encryption

Optional authenticated encryption at rest is available with:

```bash
pip install 'mistik2-memory[encryption]'
```

Use a high-entropy secret managed outside the memory directory. Encryption does not provide cryptographic erasure of old backups or protect a process that already has the live key. See [SECURITY.md](SECURITY.md).

## Installation

```bash
pip install mistik2-memory
```

Development:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

## Supported production scope

The project is designed for one logical memory store per local path and cooperating writers using the library's APIs. Linux is the most heavily validated durability/locking platform. Other supported Python platforms may have different filesystem guarantees.

Mistik2 Memory does **not** claim:

- human-equivalent or AGI memory;
- general natural-language contradiction solving;
- physical secure erasure;
- safety against an attacker with arbitrary filesystem/kernel access;
- distributed transaction semantics;
- that “grounded” evidence is objectively true in the real world.

## Documentation

- [Developer guide](docs/DEVELOPER_GUIDE.md)
- [API reference](docs/API_REFERENCE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [General memory architecture](GENERAL-MEMORY-ARCHITECTURE.md)
- [Security](SECURITY.md)
- [Durability](DURABILITY.md)
- [Upgrade guide](UPGRADING.md)
- [Release validation](RELEASE-VALIDATION.md)
- [Production readiness](PRODUCTION-READINESS.md)
- [Support](SUPPORT.md)
- [Benchmarking](BENCHMARKING.md)
- [Manifesto](MANIFESTO.md)

## Responsible use

Confirmed writes, correction approval, tombstone lifting, semantic prohibition, imports, and external-source attestation are **trusted-host capabilities**. Method names do not authenticate a person. Do not expose them directly to an untrusted model or remote caller without authorization in the host application.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
