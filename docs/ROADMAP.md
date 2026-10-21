# Ceph role maturity roadmap

## Current reassessment

This assessment is for commit `3706511` (`test: target Rocky 10 for Ceph install mock`).
At that assessed HEAD, this role is **Beta / 73% RC Readiness (floor)**
(73.5% before flooring).
The score is an engineering evidence score, not a production-suitability rating.
The scorecard below records current evidence and the gates required for full
RC readiness; planned work earns no points.

| Score area | Maximum | Current | Evidence and gap |
|---|---:|---:|---|
| Scope and public contract | 12 | 10 | Blueprint/states and test matrix are documented; general platform support remains unverified. |
| Functional completeness | 20 | 15 | Rocky 10 KVM verified bootstrap, host registration, monitor quorum and active/standby manager checks, OSDs and pool; sustained HA/failover, failure/recovery, lifecycle removal/upgrade and Rocky 9 live behavior remain unverified. |
| Validation and safety | 20 | 13 | Input validation, install-mock, device inventory guard, and scoped KVM cleanup have evidence; physical-device safety and check-mode coverage remain limited. |
| Convergence and recovery | 13 | 8 | Two live convergences and owned-unavailable OSD repeat passed; true changed reporting and failure/recovery behavior remain unverified. |
| Automated testing and CI | 25 | 20.5 | Validation, install-mock, production lint and example syntax passed; full Rocky 10 KVM eight-action sequence passed. Rocky 9 live test, failure/lifecycle coverage and established shared GitHub CI remain gaps. |
| Documentation and release hygiene | 10 | 7 | README, testing guidance and roadmap updated with accurate evidence and limitations; release and upgrade guidance remain incomplete. |
| **Total** | **100** | **73.5** | **Beta (73% floor)** |

## Evidence at assessed commit

At this assessed commit, bootstrap pins to the official Tentacle image
`quay.io/ceph/ceph:v20.2.4`, checks orchestrator device inventory before each
OSD spec, and waits up to 60 seconds for declared hosts to appear in
`ceph orch host ls`. The mock scenario exercises both accepted and rejected
device inventory. These implementation and mock-contract details, together
with the live run below, are the evidence for this assessment.
The assessed evidence includes a passing full Rocky 10 Tentacle 20.2.4
`kvm-ceph` sequence: create, first converge and verify, second converge and
verify (including owned-unavailable OSD repeat), and cleanup. Verification
observed three monitors in quorum, active and standby managers, two OSDs up/in,
the pool, and non-error health. Cleanup removed scenario guests, disks and OSDs
while preserving shared network, pool and base images. It ran with shared
environment HEAD `b6b56db`, Ansible Core 2.20.8 and Molecule 26.8.0. Validation,
install-mock, production lint and example syntax also passed. This evidence
does not demonstrate failure/recovery, upgrade/removal, true changed reporting,
Rocky 9 live support, or successful shared GitHub CI.

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
