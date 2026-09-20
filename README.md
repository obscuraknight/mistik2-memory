# mistik2-memory 1.8.0
> **Compatibility note:** the distribution/release name is `mistik2-memory`, while the Python import namespace remains `mistik_memory` so existing Mistik integrations do not break.

**Author:** panosk · **License:** Apache-2.0 · **Python:** 3.10+

Mistik2 Memory is a local, file-backed **governed personal-fact store** for companion and assistant hosts. It keeps confirmed facts distinct from inferred ones, records corrections and forgetting as durable state, and fails closed when that state cannot be trusted. It is not a general episodic memory layer, not a vector database, and not a multi-tenant service.

The library is independent of the Mistik companion application. Hosts that only need inspectable personal-fact state can import it directly. Parser coverage is a small English relation registry plus human-confirmed free prose.

**Canonical source:** https://github.com/obscuraknight/mistik2-memory

## Install

```sh
python -m pip install .
python -m pip install '.[encryption]'
python -m pip install '.[test]'
python -m pytest -q
```

## Scope and limits

Eight shipped English relations: favorite color, current city, occupation, employer, allergy, medication, pet name, scheduled event. Confirmed free prose is allowed; closed inferred admission is the default. Retrieval is BM25 plus optional embeddings. Built-in vectors are hashed character features, not a learned model.

Trusted-host APIs (`remember_fact`, `confirm`, `apply_correction`) are not an authentication system. Do not expose them as unrestricted model tools.

The unencrypted core has no runtime dependencies. Linux is the verified platform. See DURABILITY.md and SECURITY.md in the full source tree.
