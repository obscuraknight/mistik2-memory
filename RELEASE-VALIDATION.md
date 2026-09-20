# Release Validation — 2.2.0

This document records validation of the exact 2.2.0 release candidate. It is engineering evidence, not formal certification or proof against every operating system, filesystem, hardware failure, malicious host, or misuse of trusted APIs.

## Exact test inventory

**772 / 772 tests passed, 0 failed** in isolated CI-style shards.

| Validation slice | Tests | Result |
| --- | ---: | --- |
| Core, features, governance, release, supersession, forgetting, generic correction | 602 | passed |
| Persistence | 20 | passed |
| Concurrency | 27 | passed |
| Transactions | 50 | passed |
| Tombstones | 73 | passed |
| **Total** | **772** | **passed** |

The process-heavy suites are intentionally isolated. This avoids confusing long-lived multiprocessing resource exhaustion in constrained runners with a library failure.

## 2.2 production-hardening coverage

The release adds regression coverage for:

- default-deny external provenance;
- revocable external-source resolver behavior;
- one pinned generation of each derived store per inference session;
- `all` versus `any` source semantics;
- transitive source invalidation;
- semantic-update provenance replacement;
- source-linked procedural outcomes and revocation-sensitive reliability;
- timezone-normalized episodic cutoffs;
- active integrity refresh after external sidecar corruption;
- source-reference control-character/size rejection;
- symlink-resistant lock-file opening;
- owner-only atomic JSON replacement and directory-sync warning behavior.

## Packaging gates

Before the release artifact is accepted, the exact source tree is also required to pass:

- `python -m compileall -q src tests`;
- wheel and sdist build;
- clean-environment wheel install;
- `pip check`;
- package version/import verification;
- README local-link validation;
- MANIFEST explicit-file validation.

GitHub CI additionally includes dependency auditing and CodeQL analysis.

## What this evidence supports

The validated implementation is a strong local governed-memory release candidate for applications that use cooperating library writers and respect the documented trusted-host boundary.

It does **not** establish:

- distributed ACID semantics;
- arbitrary network-filesystem correctness;
- resistance to a process/kernel attacker with the encryption secret;
- physical or cryptographic erasure of backups/old blocks;
- general natural-language contradiction resolution;
- objective truth of grounded memory;
- human-equivalent or AGI memory.

Linux local filesystems remain the most heavily exercised locking/durability environment.
