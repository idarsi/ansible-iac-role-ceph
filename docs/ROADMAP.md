# Ceph role maturity roadmap

## Current reassessment

The reassessment of the `update/portable-molecule-testing` working tree, based on
`d47f2d099dba4d3b3b254754309dd2c60f4d1181`, retains **Beta / 85% RC
Readiness**, with evidence dated 2026-11-19. The score is an engineering evidence
score, not a production-suitability rating. Existing supervised Rocky 9/10 runs
and example validation remain historical evidence. The new plain direct Rocky
10/current-controller Molecule sequence passed, including collection
preservation, controlled retry, idempotence, live verification and scoped cleanup.
New Rocky 9, next-controller and supervised lifecycle acceptance remain pending.
Planned work earns no points. The prior README cited `0ebdb13` and evidence
from 2026-11-17; the prior roadmap cited `ba0b270` and 2026-11-16. Those are
historical provenance, not fresh test runs of this implementation.

The base's quick CI run `44056810198` passed; target-branch CI success is not
claimed. Branch protection and repository rules are absent, so CI enforcement
earns zero, not a pending/failing-run score. Every criterion multiplier and
category subtotal is unchanged: 12 / 17 / 14.5 / 10.5 / 22 / 9 = 85.

| Score area | Maximum | Current | Evidence and gap |
|---|---:|---:|---|
| Scope and public contract | 12 | 12 | Blueprint, states, inputs, platforms and dependencies documented; broad platform/dependency compatibility is not implied by the scoped runs. |
| Functional completeness | 20 | 17 | Rocky 9 and 10 KVM runs verified the principal CephFS workflow and controlled host-add failure/retry; arbitrary interrupted-run recovery and unclaimed lifecycle transitions remain outside verified coverage. |
| Validation and safety | 20 | 14.5 | Input and MDS identity validation, mock device guard, owned-disk KVM runs and scoped cleanup have evidence; physical-device safety, check-mode and independent ISO signature verification remain limited. |
| Convergence and recovery | 13 | 10.5 | Supervised repeat convergence reported zero changes on three guests per platform; controlled host-add retry passed, but arbitrary partial-application recovery and reliable MON/MGR/OSD changed reporting remain unverified. |
| Automated testing and CI | 25 | 22 | Podman validation/mock, lint/syntax and supervised three-node KVM on Rocky 9 and 10 have evidence; required-check enforcement is absent despite passing base CI. Broader compatibility and general failure/recovery coverage remain gaps. |
| Documentation and release hygiene | 10 | 9 | README, testing guidance, contribution contract and roadmap record scoped evidence and limitations; the corrected documentation inventory passed validation-only verification, while release/upgrade guidance remains incomplete. |
| **Total** | **100** | **85** | **Beta** |

Criterion-level reconstruction of the retained score (not a recovered historical
criterion ledger), in the maturity rubric's order:

| Area | Awarded criterion points |
|---|---|
| Scope | Purpose 3; inputs/states 5; support 4 |
| Functional | Core 8; applicable lifecycle 6; platform/dependencies 1.5; failure/rerun 1.5 |
| Validation | Preflight 6; secure behavior 6; destructive guardrails 2.5; check/diff 0 |
| Recovery | Idempotence 2.5; applicable transitions 4; operational recovery 4 (narrow controlled host-add retry only, not arbitrary interruption) |
| Testing | Static 3; validation 4; functional 6; idempotence 4; lifecycle/guardrails 2; platforms 3; CI enforcement 0 |
| Documentation | Operator 4; tests/limitations 2; contribution 2; release metadata 1 |

Remaining RC blockers include check/diff behavior, accurate MON/MGR/OSD changed
reporting, physical-device eligibility and TOCTOU safety, broader interruption
guardrails, dependency compatibility, enforced CI and release policy.
Unsupported removal and upgrade features are not required merely to raise the
score. Significant coverage gaps cap the state at Beta; production approval
has not been established.

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

## Direct lifecycle acceptance (2026-11-19)

Plain `molecule test -s kvm-ceph` passed without an outer runner on three Rocky
10 guests, using Python 3.12.16, Ansible Core 2.20.8, Molecule 26.8.0 and the
updated shared helpers selected through `IDARSI_TEST_ENVIRONMENT`. Dependency,
initial destroy, syntax, create, converge, idempotence, verify and final destroy
passed. Private `ansible.posix` 2.1.0 installation survived initial
destroy/pruning and remained pinned after final pruning. Controlled host-add
rescue/retry succeeded, with subsequent `changed=0` on all three guests.
Verification covered quorum, MGR, OSD/pool/health, active CephFS, persistent
client mounts and cross-node access. Final inspection confirmed zero owned
guests/network, sealed create/destroy operations, no active generation and
preservation of pre-existing foreign resources.

This closes the pending direct Rocky 10/current-controller acceptance claim,
not the separate new Rocky 9, next-controller or supervised acceptance claims.
Shared supervised-admission fixes remain separately gated. There is meaningful
functional and idempotence evidence, so no Alpha cap applies; remaining
coverage gaps retain the Beta cap and no production approval is established.
The score remains 85; successful scoped acceptance is not an automatic score
increase.
