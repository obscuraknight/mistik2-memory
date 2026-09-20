# Security Policy

## Supported versions

Security fixes target the current release line. Older releases may not receive backports when the affected storage or governance contract has changed materially.

## Reporting a vulnerability

Use GitHub private vulnerability reporting for this repository when available. Do not post real memory stores, user transcripts, encryption secrets, access tokens, or private provenance data in a public issue.

A useful report includes the affected version/platform, synthetic reproduction data, expected vs observed behavior, and whether the issue requires filesystem access, a cooperating writer, a trusted-host API, or an untrusted model/tool caller.

## Trust boundaries

Mistik2 Memory is a local memory library. It is **not** an authentication or authorization system.

The host application must authorize access to trusted operations including:

- confirmed writes/imports;
- correction approval;
- tombstone lifting;
- exact forgetting and semantic prohibition;
- migration/seed APIs;
- external-source attestation.

Do not expose those APIs directly as unrestricted model tools.

## Derived-memory governance

Derived memories require typed sources. `fact:`, `episode:`, `semantic:`, and `procedure:` sources are resolved through refreshed governed snapshots.

`external:` sources are denied by default. A production host must pass an `external_source_resolver` to `GeneralMemorySystem`. The resolver is an application trust boundary: the library can enforce the resolver's decision, but it cannot prove an external system is truthful.

Each inference session pins one generation of the governed core IDs and each derived store. Transitive source validation uses those pinned records. Concurrent changes are observed on the next inference operation.

## Filesystem threat model

The library hardens normal local use with owner-only files, atomic same-directory replacement, sidecar locks, fail-closed parsing, and POSIX `O_NOFOLLOW` lock-file opening when available.

It does not defend against an attacker who can arbitrarily modify process memory, replace files/directories with sufficient privilege, read the encryption secret, control the kernel, or bypass the library with a non-cooperating writer.

Use a private storage directory with restrictive ownership and permissions. Do not place a sensitive store in a world-writable directory.

## Encryption at rest

The optional encryption extra uses authenticated encryption for supported store files. Treat `encryption_secret` as a high-entropy secret, not a memorable password. Store it outside the memory directory using the platform's secret-management mechanism.

Encryption does not provide:

- per-fact cryptographic erasure;
- deletion of old plaintext/ciphertext backups;
- protection from a process that already holds the live secret;
- filesystem-sector secure erase.

Legacy encrypted formats remain readable for compatibility. See `DURABILITY.md` and `UPGRADING.md`.

## Availability and resource limits

The library validates schema and source references, but a trusted host can still create very large stores. Deployments should apply their own quotas for users, messages, external-source identifiers, disk usage, and request rate.

## Dependencies

The unencrypted core has no required third-party runtime dependencies. Encryption uses `cryptography`. CI includes dependency auditing and CodeQL analysis for the repository release line.
