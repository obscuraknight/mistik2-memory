# Developer Guide

## Install

```bash
pip install mistik2-memory
```

```python
from mistik_memory import LongTermMemory, StorageContext

ctx = StorageContext.from_root("alice", "./data/alice")
core = LongTermMemory(storage_context=ctx)
```

## Trusted factual writes

```python
core.remember_fact(
    "The user lives in Berlin.",
    provenance={"source_message_id": "msg-42", "source_session_id": "session-7"},
)
```

`remember_fact()` is a trusted-host API. The method name does not authenticate a human.

## Derived memory

```python
from mistik_memory import GeneralMemorySystem

memory = GeneralMemorySystem(core)
fid = core.read_view()["facts"][0]["fact_id"]

eid = memory.episodic.remember(
    "The Berlin relocation was completed.",
    source_ids=[f"fact:{fid}"],
)

sid = memory.semantic.remember(
    "Berlin relocation",
    "A relocation concept backed by the episode.",
    source_ids=[f"episode:{eid}"],
)
```

Every derived write requires sources. `source_policy="all"` is the default. Use `source_policy="any"` only for independently sufficient evidence.

## External sources

External sources are denied unless the host supplies a resolver.

```python
trusted = {"calendar:evt-42"}
memory = GeneralMemorySystem(
    core,
    external_source_resolver=lambda source_id: source_id in trusted,
)
```

Revoking an ID from the resolver suppresses dependent derived inference on the next read.

## Correct an exact fact

```python
old = next(f for f in core.read_view()["facts"] if "blue cotton" in f["text"])
core.correct_fact_version(
    old["fact_id"],
    "The recovered fibers were indigo conservation linen.",
    provenance={"source_component": "forensic_lab"},
)
```

## Forgetting vs prohibition

```python
core.forget_fact_version(fact_id)                 # one identity
core.prohibit_fact_pattern("The user lives in Paris.")  # broader semantic ban
```

## Procedure outcomes

```python
pid = memory.procedural.remember(
    "Restart service",
    ["stop", "start", "verify"],
    source_ids=[f"fact:{runbook_id}"],
)

memory.procedural.record_outcome(
    pid,
    success=True,
    source_ids=[f"fact:{incident_result_id}"],
)
```

If the outcome source is later invalidated, the outcome no longer contributes to governed reliability.

## Production checklist

- one logical user/store per private storage path;
- authorize trusted mutation APIs in the host;
- supply a revocable resolver for `external:` provenance;
- monitor `GeneralMemorySystem.integrity()`;
- keep encryption secrets outside the memory directory;
- set disk/request quotas in the host application;
- read `SECURITY.md`, `DURABILITY.md`, and `UPGRADING.md` before deployment.
