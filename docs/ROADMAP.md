# Ceph role maturity roadmap

## Current reassessment

This assessment is for the uncommitted current working tree on branch
`update/cephfs-support`, based on HEAD `8ae3a38`, including the two uncommitted
MDS identity validation and install-mock changes. This role is
**Beta / 81% RC Readiness (81.5 before floor)**.
The score is an engineering evidence score, not a production-suitability rating.
The scorecard below records current evidence and the gates required for full
RC readiness; planned work earns no points.

| Score area | Maximum | Current | Evidence and gap |
|---|---:|---:|---|
| Scope and public contract | 12 | 10 | Blueprint, states, inputs, and test matrix are documented; broader platform/dependency support remains unverified. |
| Functional completeness | 20 | 17 | Rocky 10 KVM evidence verifies the principal live CephFS workflow; lifecycle transitions, Rocky 9 live behavior, and failure/recovery remain unverified. |
| Validation and safety | 20 | 15 | Input and MDS identity validation, install-mock, device inventory guard, scoped KVM cleanup, and CephFS client safety have evidence; physical-device safety and check-mode coverage remain limited. |
| Convergence and recovery | 13 | 10 | KVM repeat convergence produced zero changes; failure recovery and accurate changed reporting remain unverified. |
| Automated testing and CI | 25 | 22 | Validation, install-mock (including MDS identity cases), production lint, example syntax, and live KVM evidence exist; lifecycle/failure and Rocky 9 live coverage remain gaps. CI result enforcement at this ref remains unverified. |
| Documentation and release hygiene | 10 | 7 | README, testing guidance and roadmap updated with accurate evidence and limitations; release and upgrade guidance remain incomplete. |
| **Total** | **100** | **81.5** | **Beta (81% floor)** |

## Evidence at assessed commit

At this assessed working tree on `update/cephfs-support`, based on HEAD
`8ae3a38`, including the uncommitted MDS identity validation and install-mock
changes, bootstrap pins to the official Tentacle image
`quay.io/ceph/ceph:v20.2.4`, checks orchestrator device inventory before each
OSD spec, and waits up to 60 seconds for declared hosts to appear in
`ceph orch host ls`. The mock scenario exercises both accepted and rejected
device inventory. These implementation and mock-contract details, together
with the live run below, are the evidence for this assessment.
Fresh assessed evidence includes a passing eight-action Rocky 10 Tentacle 20.2.4
`kvm-ceph` CephFS sequence: create, converge and verify, repeat converge and
verify with zero changes, then cleanup. Verification covered CephFS filesystem
and active MDS, client credentials and persistent kernel mounts on declared
clients, including cross-node mounts. Cleanup removed scenario guests, disks,
OSDs and mounts while preserving shared resources. It ran with shared
environment HEAD `b6b56db`, Ansible Core 2.20.8 and Molecule 26.8.0. Validation,
install-mock, production lint and example syntax also passed. This evidence
does not demonstrate failure/recovery, upgrade/removal, or Rocky 9 live support;
Rocky 9 remains unsupported by live evidence. CI result enforcement at this ref
is unverified. None of this evidence establishes production suitability.

Version source: [Ceph Tentacle release notes](https://docs.ceph.com/en/latest/releases/tentacle/)
identify v20.2.4 (released 2026-08-19) as the current stable Tentacle release
and recommend it. Service-spec and device-availability behavior is based on
the [Tentacle OSD service documentation](https://docs.ceph.com/en/tentacle/cephadm/services/osd)
and [cephadm deployment documentation](https://docs.ceph.com/en/tentacle/cephadm/install).
The role installs bootstrap prerequisites and the official cephadm executable
from the pinned `rpm-20.2.4/el9/noarch/cephadm` source URL on the designated
bootstrap host. It uses the pinned container image for daemon version selection.

Rocky 9 live-cluster behavior remains untested. Rocky 10 has a successful KVM
run, but this does not establish broad platform support; the role consumes an
upstream EL9 cephadm artifact on Rocky 10, whose compatibility remains a caveat.

## Milestones and acceptance gates

Each gate requires committed evidence and refreshed README/TESTING claims. A
mock is useful for command contract testing but cannot substitute for a cluster.

1. **Mocked install contract (focused, no cluster) — complete at assessed HEAD:** use temporary stub
   `cephadm` and `ceph` executables to inspect bootstrap arguments and generated
   JSON service specs, and exercise two install passes. Verify local bootstrap
   and pool guards, and accurately report task changes. Never mock device
   discovery/safety, claim OSD data safety, quorum, or HA. This is a narrow
   functional test only. Validation and install-mock passed at assessed HEAD;
   these are not evidence of true idempotence or live Ceph behavior.
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

Mocks can validate argument construction, generated specs, and guards. The
successful KVM run provides real cluster convergence and scoped cleanup evidence,
but does not establish disk eligibility/data safety, failure recovery, upgrade
or removal behavior, or accurate changed reporting. Production-like evidence
and Rocky 9 live testing remain absent; these are required before recommending
production use or assigning Stable/Mature status.
