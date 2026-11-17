# Ceph role maturity roadmap

## Current reassessment

The reassessment of `update/ceph-kvm-recovery-tests` (this change, based on
`ba0b270`; supervised evidence from 2026-11-16) is **Beta / 85% RC
Readiness**. The linked example passed local validation-only verification.
The score is an engineering evidence score, not a production-suitability rating.
The scorecard includes both supervised Rocky 9 and Rocky 10 runs; planned work
earns no points.

| Score area | Maximum | Current | Evidence and gap |
|---|---:|---:|---|
| Scope and public contract | 12 | 12 | Blueprint, states, inputs, platforms and dependencies documented; broad platform/dependency compatibility is not implied by the scoped runs. |
| Functional completeness | 20 | 17 | Rocky 9 and 10 KVM runs verified the principal CephFS workflow and controlled host-add failure/retry; arbitrary interrupted-run recovery and unclaimed lifecycle transitions remain outside verified coverage. |
| Validation and safety | 20 | 14.5 | Input and MDS identity validation, mock device guard, owned-disk KVM runs and scoped cleanup have evidence; physical-device safety, check-mode and independent ISO signature verification remain limited. |
| Convergence and recovery | 13 | 10.5 | Supervised repeat convergence reported zero changes on three guests per platform; controlled host-add retry passed, but arbitrary partial-application recovery and reliable MON/MGR/OSD changed reporting remain unverified. |
| Automated testing and CI | 25 | 22 | Podman validation/mock, lint/syntax and supervised three-node KVM on Rocky 9 and 10 have evidence; CI result enforcement, broader compatibility and general failure/recovery coverage remain gaps. |
| Documentation and release hygiene | 10 | 9 | README, testing guidance, contribution contract and roadmap record scoped evidence and limitations; the corrected documentation inventory passed validation-only verification, while release/upgrade guidance remains incomplete. |
| **Total** | **100** | **85** | **Beta** |

## Prior 81% assessment (historical)

At assessed commit `a607c7f63ba2e93761ea94ed03e1025d8bc4fe7d` on
`update/cephfs-support`, bootstrap pins to the official Tentacle image
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
podman-install-mock, production lint and example syntax also passed under the
scenario's former name. This evidence
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

At this historical assessed commit, Rocky 9 live-cluster behavior was untested.
Rocky 10 had a successful custom KVM run, but this did not establish broad
platform support; the role consumes an upstream EL9 cephadm artifact on Rocky
10, whose compatibility remains a caveat.

## Supervised KVM evidence (included in current scorecard)

On `update/ceph-kvm-recovery-tests`, supervised `kvm-ceph` runs passed and
cleaned on Rocky 9 (`613a2ea1-8486-46a4-aeef-f1da535a4de0`) and Rocky 10
(`ba66c9ce-be15-42a5-b151-fee0b135a66d`). Each verified a root-only ISO
installation guard, a serial-qualified owned OSD device reported in Ceph
inventory, controlled `ceph-b` host-add failure and successful retry, three
monitors and three OSDs up/in, manager and CephFS cross-node persistent mounts,
and `changed=0` on all three guests at idempotence. Both supervisors reported
zero owned guest/network records after cleanup; Rocky 10 `virsh` guest/network
listings were also empty. Official HTTPS ISO hashes matched checksum files,
but the checksum files were not signature-verified. Two older pre-policy
resources remain retained outside these runs. This evidence closes the
previously untested managed-sequence and Rocky 9 live-run claims, not the
broader device-safety, arbitrary or interrupted-run recovery, upgrade/removal,
changed-reporting, CI-enforcement or production-readiness gaps. See
[TESTING.md](../TESTING.md).

## Milestones and acceptance gates

Each gate requires committed evidence and refreshed README/TESTING claims. A
mock is useful for command contract testing but cannot substitute for a cluster.

1. **Mocked install contract (focused, no cluster) — complete at assessed HEAD:** use temporary stub
   `cephadm` and `ceph` executables to inspect bootstrap arguments and generated
   JSON service specs, and exercise two install passes. Verify local bootstrap
   and pool guards, and accurately report task changes. Never mock device
   discovery/safety, claim OSD data safety, quorum, or HA. This is a narrow
   functional test only. Validation and podman-install-mock passed at assessed HEAD
   under their former scenario names;
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
historical and newer supervised KVM runs provide real cluster convergence and
scoped cleanup evidence; the latter also verify controlled host-add failure
recovery on Rocky 9 and 10. They do not establish physical-device
eligibility/data safety, arbitrary interrupted-run recovery, upgrade or
removal behavior, or accurate changed reporting. Production-like evidence
remains absent; these gaps preclude recommending production use or assigning
Stable/Mature status.
