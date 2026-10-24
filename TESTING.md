# Testing

This Beta release has validation and mock-CLI scenarios plus a guarded live
multi-host KVM integration scenario. Historical validation, install-mock,
production-profile lint, example syntax, and the then-current KVM sequence passed
at commit `3706511`; that KVM evidence predates the current CephFS coverage.
At assessed commit `a607c7f63ba2e93761ea94ed03e1025d8bc4fe7d` on
`update/cephfs-support`, validation, install-mock, production-profile lint, and
example syntax passed. The latest Rocky 10 Tentacle 20.2.4 `kvm-ceph` Molecule sequence passed
all eight actions (create, converge/verify twice, cleanup) using shared
environment HEAD `b6b56db`, Ansible Core 2.20.8, and Molecule 26.8.0. The live
run verified three OSDs, an active MDS, `ceph-common`/`mount.ceph`, persistent
mounts across all three clients, cross-node write/read, second convergence with
`changed=0`, and scoped cleanup. These results do not establish general Rocky 10
support or Rocky 9 live-cluster support.
The mock scenario checks
command arguments/spec generation, bootstrap's local guard, accepted/rejected
OSD device inventory (including duplicate ambiguous records), bootstrap SSH-user arguments, and public-key installation for declared peers, and two install passes in one converge play without a Ceph cluster. Mock state and the overridden bootstrap sentinel are confined to `/tmp/ceph-mock-state` in the unmounted Podman container. The
scenario deliberately omits Molecule's separate idempotence phase: its second
install pass is the explicit repeat-install check, using persisted mock host
registration and pool state. It does not verify Ceph
acceptance/convergence, disk safety, OSD provisioning, HA, or platform support.

| Platform/image | Ansible or application versions | Molecule scenarios | Main coverage |
|---|---|---|---|
| Rocky Linux 9 Podman container | Ansible Core >=2.19 | validation — passed at 3706511 historically; passed at assessed commit `a607c7f` | Accepted and rejected blueprint inputs; validation-only non-mutation. Container validation is not Rocky 9 live-platform evidence. |
| Rocky Linux 10 / Python 3.12 Podman container | Ansible Core >=2.19 | install-mock — passed at 3706511 historically; passed at assessed commit `a607c7f` | Installed cephadm version check, prerequisite package task (container mock skips chronyd), pool conflict preflight, accepted/rejected OSD inventory, duplicate/count and identity cases, pinned image and repeated mocked install; not platform support evidence. |
| Rocky Linux 10 KVM guests (three-node cluster) | Ceph Tentacle 20.2.4; Ansible Core 2.20.8; Molecule 26.8.0 | kvm-ceph — full eight-action CephFS sequence passed at assessed commit `a607c7f` | Three monitors, active and standby manager, three scenario-owned OSDs up/in, pool (`pg_num: 32`, matching the autoscaler-adjusted value observed by KVM diagnostics), non-error health, CephFS with active MDS, `ceph-common` and `mount.ceph` on all three clients, persistent mounts on all nodes, cross-node write/read, second convergence with `changed=0`, and scoped cleanup. |

| Rocky Linux 9 KVM guests (three-node cluster) | Ceph Tentacle 20.2.4; Ansible Core >=2.19 | kvm-ceph — not run | Intended test target only; no live-cluster evidence. |

CephFS clients receive the matching Ceph Tentacle RPM repository from
`https://download.ceph.com/rpm-<ceph_version>/el<major>/$basearch` before
`ceph-common` installation. Repository TLS verification and RPM signature
checking remain enabled using the official Ceph release key. Client operating
system facts are gathered and validated individually before install mutations.
The delegated `ceph-common` package installation retries up to four times with
15 seconds between attempts for transient repository/network failures; exhausted
attempts remain a task failure.
Only declared client hosts receive signed `epel-release` from Rocky Extras and
have CRB enabled using `crb enable`, followed by the pinned Ceph package
repository and `ceph-common` installation. Missing CRB tooling fails with a
clear error. An empty client list configures no client repository, enables no
extra repository, and installs no client packages.
The `epel-release` installation also retries up to four times with 15 seconds
between attempts for transient Rocky Extras mirror/network failures.

The install-mock scenario checks the exact `ceph fs volume create <name>` CLI
(without an invalid MDS-count positional argument), exact JSON MDS orchestrator
specification, first-pass MDS apply and second-pass skip, and repeat-install
volume idempotence. Its first two-pass install
asserts seven daemon applies total, with the MDS specification submitted only
once and readiness polled twice while creating/active, then once more on the
repeat install. An isolated MDS-only install uses the already matching exported
specification and verifies the MDS apply is skipped without OSD or pool
blueprint resources. The invalid boolean MDS-count export remains a separate
preflight regression. Existing matching MDS specifications with unsupported
placement fail before service-spec, pool/filesystem, and client convergence;
host setup, bootstrap, and registration may already have occurred. Unrelated
MDS specs with host placement remain valid. MDS service IDs are required to be
strings before matching. It
includes focused
Tentacle `mon dump` fixtures through the same normalization task file used by
install: v2 preference with v1 fallback, an endpoint with a nonce suffix, and
bracketed IPv6. The mocked `ceph mds stat` response transitions the declared
filesystem from `creating` to `up:active` while another filesystem is already
active, verifying readiness is scoped to the exact filesystem-name prefix.
Install readiness polls for at most 30 attempts with 10-second delays before
any CephFS client package, directory, or mount mutations. KVM verification uses
the same MDS status filter and loads it from the role's `filter_plugins`.
The install-mock scenario exercises protocol-aware monitor normalization:
dual-stack and mixed-capability monitor sets select only v2 with `prefer-secure`,
while v1-only sets fall back to `legacy`. The validation scenario covers the
CephFS blueprint's MDS count, client host, filesystem
reference, client identity, accepted `/srv/...` and `/mnt/...` mountpoints, and
rejected root/system-tree, traversal, empty-component, and unsafe-character
forms. During install, each client mountpoint is resolved with `realpath -m`
before package, directory, or mount changes; changed resolutions (including
symlink ancestors) are rejected.

Use the pre-existing shared `idarsi-ansible-test-environments` environment; follow that repository's setup instructions to activate it.

The `install-mock` and `kvm-ceph` scenarios each install their pinned
`ansible.posix` collection (`molecule/*/requirements.yml`) through Molecule's
Galaxy dependency step; no shared Ansible environment dependency is changed.

The live KVM scenario is deliberately excluded from PR/push CI. It is a
manual/scheduled heavy test requiring libvirt/KVM, an available Rocky Linux ISO,
and disposable storage. After activating `ansible-current` from the shared
environment and confirming the `idarsi-test-bases` storage pool and shared
`idarsi-test` network:

```bash
export IDARSI_TEST_KVM_INSTALL_SOURCE=/path/to/Rocky-10-x86_64-dvd.iso
export IDARSI_CEPH_KVM_DISPOSABLE=YES_I_WILL_DESTROY_THESE_VMS_AND_DISKS
molecule test -s kvm-ceph
```

The exact acknowledgment is required by both create and destroy. Before
bootstrap or host registration, the role installs Podman, LVM2, chrony, and
Python 3 on every unique declared monitor/OSD host, then enables/starts chronyd
on systemd hosts. Undeclared inventory hosts are not targeted. The scenario
uses static addresses `.21`–`.23` on the shared NAT network and creates three
named ephemeral OSD volumes in the active `idarsi-test-bases` pool
(override with `IDARSI_CEPH_OSD_VOLUME_POOL` if needed); it removes those
volumes and the three shared-lifecycle guests at teardown. Never run it against valuable VMs
or storage. Rocky 10 has passed this sequence; Rocky 9 live-cluster behavior has not been
tested. A Rocky 9 ISO can be substituted for a compatibility attempt, but Rocky 9 is not
yet supported or verified for this live-cluster test. Shared environment setup and state
can differ between runs; confirm disposable guests/storage and required shared network/pool
before execution.

Commands: `molecule test -s validation`; `molecule test -s install-mock`; `ansible-lint --profile production`; `ansible-playbook --syntax-check -i docs/inventory-minimal.yml docs/playbook-example.yml`.

KVM evidence establishes the tested cluster outcomes and scoped teardown only. It does not establish failure/recovery, upgrade/removal, or accurate changed reporting for MON/MGR/OSD specs; repeated specs may report `changed: false` without reliable state comparison. MDS reconciliation uses placement-count matching, not general cluster-state comparison. It does not prove device safety or Rocky 9 support. Shared GitHub CI enforcement has not been established. Real failure/recovery, upgrade/removal, MON/MGR/OSD changed reporting, supported-platform matrix, and production-like evidence remain gaps. Podman backend is expected; Docker is not supported. See [ROADMAP.md](docs/ROADMAP.md).

The prior Rocky 9 / Python 3.9 install-mock incompatibility was addressed by
running install-mock on Rocky 10 / Python 3.12. At 3706511, configured
validation, mock, lint, and syntax checks passed locally; the same focused
checks passed at assessed commit `a607c7f`. `.github/workflows/quick.yml`
defines PR/push checks, but successful shared GitHub Actions enforcement has
not been established. Rocky 9 live cluster and Rocky 10 general platform
compatibility remain unverified; the cephadm executable is sourced from the
upstream EL9 artifact, a compatibility caveat on Rocky 10.
