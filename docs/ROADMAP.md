# Ceph role maturity roadmap

## Current reassessment

This assessment is for commit `81bae73` (`Fix missing account rescue assertion`).
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
| Automated testing and CI | 25 | 8 | An earlier validation/install-mock run at `50fb` passed, but the latest run at assessed HEAD failed before scenario actions because the shared `ansible-current` Podman plugin rejects `containers.podman.podman_image` `build.file`. Production-profile lint passes. The failure earns no scenario credit for current HEAD; install-mock and KVM behavior remain unverified. Mocks cannot establish true idempotence, actual Ceph execution, or live cluster, HA, OSD/device-safety behavior; required CI evidence is missing. |
| Documentation and release hygiene | 10 | 8 | README, testing guidance/limitations, and this evidence-based roadmap document role usage and boundaries. Supported-platform/dependency policy and complete contribution, release, and upgrade guidance remain gaps. |
| **Total** | **100** | **52** | **Alpha (floor)** |

## Progress since the assessed commit

The implementation now pins bootstrap to the official Tentacle image
`quay.io/ceph/ceph:v20.2.4`, checks orchestrator device inventory before each
OSD spec, and waits up to 60 seconds for declared hosts to appear in
`ceph orch host ls`. The mock scenario exercises both accepted and rejected
device inventory. These are implementation and mock-contract improvements,
not evidence of a live Ceph deployment or an updated maturity score.

Version source: [Ceph Tentacle release notes](https://docs.ceph.com/en/latest/releases/tentacle/)
identify v20.2.4 (released 2026-08-19) as the current stable Tentacle release
and recommend it. Service-spec and device-availability behavior is based on
the [Tentacle OSD service documentation](https://docs.ceph.com/en/tentacle/cephadm/services/osd)
and [cephadm deployment documentation](https://docs.ceph.com/en/tentacle/cephadm/install).
The role installs bootstrap prerequisites and the official cephadm executable
from the pinned `rpm-20.2.4/el9/noarch/cephadm` source URL on the designated
bootstrap host. It uses the pinned container image for daemon version selection.

The latest real Rocky 10 run passed bootstrap but failed SSH root authentication
before the new nonroot key-distribution implementation. That implementation
has not been tested by this run. Rocky Linux 9/10 support remains unverified.
The KVM scenario cannot currently run because the shared `idarsi-test` network
and `idarsi-test-bases` storage pool are absent; no shared environment changes
were made.

## Milestones and acceptance gates

Each gate requires committed evidence and refreshed README/TESTING claims. A
mock is useful for command contract testing but cannot substitute for a cluster.

1. **Mocked install contract (focused, no cluster) — complete at assessed HEAD:** use temporary stub
   `cephadm` and `ceph` executables to inspect bootstrap arguments and generated
   JSON service specs, and exercise two install passes. Verify local bootstrap
   and pool guards, and accurately report task changes. Never mock device
   discovery/safety, claim OSD data safety, quorum, or HA. This is a narrow
   functional test only. A prior run at `50fb` passed validation and install-mock,
   but the latest Molecule attempt at assessed HEAD failed before scenario
   actions due to the shared Podman plugin's unsupported `build.file` argument.
   Neither current scenario is thereby verified; this is not evidence of live
   Ceph behavior or true idempotence.
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
