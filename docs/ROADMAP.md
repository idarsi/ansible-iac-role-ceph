# Ceph role maturity roadmap

## Current reassessment

This assessment is for commit `79df116` (`test: assert validation safety and host convergence`).
At that assessed HEAD, this role is **Alpha / 52% RC Readiness (floor)**.
The score is an engineering evidence score, not a production-suitability rating.
The scorecard below records current evidence and the gates required for full
RC readiness; planned work earns no points.

| Score area | Maximum | Current | Evidence and gap |
|---|---:|---:|---|
| Scope and public contract | 12 | 9 | Blueprint and state limits are documented; platform and dependency/support evidence is incomplete. |
| Functional completeness | 20 | 10 | Bootstrap and declared operations exist; actual Ceph execution, platform, recovery, and asynchronous convergence remain unverified. |
| Validation and safety | 20 | 12 | Input preflight and explicit OSD opt-in are implemented and covered by validation/mock scenarios; comprehensive proof that every failure precedes mutation, physical-device safety, and check-mode behavior are not established. |
| Convergence and recovery | 13 | 5 | Bootstrap/pool guards exist; orchestration specs are reapplied and external convergence is not observed. |
| Automated testing and CI | 25 | 8 | Validation and mocked install Molecule coverage exercise input guards, generated command/spec contracts, and repeat-install reporting. The mocks do not establish true idempotence, actual Ceph execution, or live cluster, HA, OSD/device-safety behavior; a supported-platform matrix and evidenced required CI are missing. |
| Documentation and release hygiene | 10 | 8 | README, testing guidance/limitations, and this evidence-based roadmap document role usage and boundaries. Supported-platform/dependency policy and complete contribution, release, and upgrade guidance remain gaps. |
| **Total** | **100** | **52** | **Alpha (floor)** |

## Milestones and acceptance gates

Each gate requires committed evidence and refreshed README/TESTING claims. A
mock is useful for command contract testing but cannot substitute for a cluster.

1. **Mocked install contract (focused, no cluster) — complete at assessed HEAD:** use temporary stub
   `cephadm` and `ceph` executables to inspect bootstrap arguments and generated
   JSON service specs, and exercise two install passes. Verify local bootstrap
   and pool guards, and accurately report task changes. Never mock device
   discovery/safety, claim OSD data safety, quorum, or HA. This is a narrow
   functional test only. The validation and install-mock Molecule scenarios
   passed; this is not evidence of live Ceph behavior or true idempotence.
2. **Command/change semantics:** capture actual `ceph orch apply` effects or
   expose a reliable comparison workflow before claiming changed-state
   accuracy or idempotence for placement/OSD specs. Verify host registration
   behavior against Ceph's real response semantics; avoid unconditional
   `changed: true` where no mutation occurs.
3. **Validation and safety:** verify validation fails before all mutations;
   add safe check-mode behavior or narrowly guard unsupported CLI operations.
   Establish actual device-eligibility controls before any stronger OSD safety
   promise. Do not erase, zap, or otherwise fake destructive-device coverage.
4. **Functional cluster evidence:** provision disposable multi-host KVM
   environments with real supported Ceph/cephadm versions. Verify bootstrap,
   host registration, monitor/manager placement, declared OSD workflow on
   explicitly disposable devices, pool behavior, asynchronous completion,
   reruns, interrupted-run recovery, and removal boundaries. Record topology,
   versions, logs/results, and cleanup. No mock substitutes for these gates.
5. **Support and release engineering:** test every claimed OS/version and
   relevant Ansible compatibility boundary; align platform claims to evidence.
   Add focused PR CI and scheduled/release coverage for the full scenarios,
   production lint/syntax checks, dependency and metadata policy, and a
   reviewed upgrade/recovery path.
6. **Independent RC review:** close every scorecard gap with reproducible
   evidence, review security/destructive behavior and operational recovery,
   and obtain independent review. Only then reassess all criteria; 100% is a
   gate, not a forecast or a claim made by this roadmap.

## RC is not Stable or Mature

**Release Candidate** requires a 100% engineering score, complete documented
contract, passing applicable checks, and no known RC blocker. It is not itself
approval for production use. **Stable** additionally requires a recorded human
production-readiness decision against a reviewed commit, including
production-like deployment, upgrade/rerun/recovery/removal, security review,
ownership, and compatibility policy. **Mature** additionally requires at least
twelve months of credible production use, routine maintenance/upgrade evidence,
real operational recovery evidence, and no unresolved pattern of severe
regressions.

## Evidence limitation

Mocks can validate argument construction, generated specs, guards, and
Ansible's local changed reporting. They cannot demonstrate Ceph accepting or
converging those specs, disk eligibility or data safety, network behavior,
quorum, availability, or recovery under real failure. The role has no
independently established real multi-host KVM or production-like evidence.
Such evidence is required before recommending production use or assigning
Stable/Mature status.
