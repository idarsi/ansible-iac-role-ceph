# Testing

This Beta release has validation and mock-CLI scenarios plus a guarded live
multi-host KVM integration scenario. At assessed commit `3706511`, validation,
install-mock, production-profile lint, and example syntax checks passed. The
full Rocky 10 Tentacle 20.2.4 `kvm-ceph` Molecule sequence also passed all eight
actions (create, converge/verify twice, cleanup) using shared environment HEAD
`b6b56db`, Ansible Core 2.20.8, and Molecule 26.8.0. These results do not
establish general Rocky 10 support or Rocky 9 live-cluster support.
The mock scenario checks
command arguments/spec generation, bootstrap's local guard, accepted/rejected
OSD device inventory (including duplicate ambiguous records), bootstrap SSH-user arguments, and public-key installation for declared peers, and two install passes in one converge play without a Ceph cluster. Mock state and the overridden bootstrap sentinel are confined to `/tmp/ceph-mock-state` in the unmounted Podman container. The
scenario deliberately omits Molecule's separate idempotence phase: its second
install pass is the explicit repeat-install check, using persisted mock host
registration and pool state. It does not verify Ceph
acceptance/convergence, disk safety, OSD provisioning, HA, or platform support.

| Platform/image | Ansible or application versions | Molecule scenarios | Main coverage |
|---|---|---|---|
| Rocky Linux 9 Podman container | Ansible Core >=2.19 | validation — passed at 3706511 | Accepted and rejected blueprint inputs; validation-only non-mutation. Container validation is not Rocky 9 live-platform evidence. |
| Rocky Linux 10 / Python 3.12 Podman container | Ansible Core >=2.19 | install-mock — passed at 3706511 | Installed cephadm version check, prerequisite package task (container mock skips chronyd), pool conflict preflight, accepted/rejected OSD inventory, pinned image and repeated mocked install; not platform support evidence. |
| Rocky Linux 10 KVM guests (three-node cluster) | Ceph Tentacle 20.2.4; Ansible Core 2.20.8; Molecule 26.8.0 | kvm-ceph — full sequence passed at 3706511 | Three monitors in quorum, active and standby manager, two scenario-owned OSDs up/in, pool, non-error health, second convergence including owned-unavailable OSD repeat, and scoped cleanup. Cleanup removed scenario guests/disks/OSDs and preserved shared network, pool, and base images. |
| Rocky Linux 9 KVM guests (three-node cluster) | Ceph Tentacle 20.2.4; Ansible Core >=2.19 | kvm-ceph — not run | Intended test target only; no live-cluster evidence. |

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
uses static addresses `.21`–`.23` on the shared NAT network and creates only
two named ephemeral OSD volumes in the active `idarsi-test-bases` pool
(override with `IDARSI_CEPH_OSD_VOLUME_POOL` if needed); it removes those
volumes and the three shared-lifecycle guests at teardown. Never run it against valuable VMs
or storage. Rocky 10 has passed this sequence; Rocky 9 live-cluster behavior has not been
tested. A Rocky 9 ISO can be substituted for a compatibility attempt, but Rocky 9 is not
yet supported or verified for this live-cluster test. Shared environment setup and state
can differ between runs; confirm disposable guests/storage and required shared network/pool
before execution.

Commands: `molecule test -s validation`; `molecule test -s install-mock`; `ansible-lint --profile production`; `ansible-playbook --syntax-check -i docs/inventory-minimal.yml docs/playbook-example.yml`.

KVM evidence establishes the tested cluster outcomes and scoped teardown only. It does not establish failure/recovery, upgrade/removal, or accurate changed reporting; repeated specs may report `changed: false` without reliable state comparison. It does not prove device safety or Rocky 9 support. Shared GitHub CI has not been established. Real failure/recovery, upgrade/removal, true changed reporting, supported-platform matrix, and production-like evidence remain gaps. Podman backend is expected; Docker is not supported. See [ROADMAP.md](docs/ROADMAP.md).

The prior Rocky 9 / Python 3.9 install-mock incompatibility was addressed by
running install-mock on Rocky 10 / Python 3.12. At 3706511, configured
validation, mock, lint, and syntax checks passed locally. `.github/workflows/quick.yml`
defines PR/push checks, but successful shared GitHub Actions enforcement has
not been established. Rocky 9 live cluster and Rocky 10 general platform
compatibility remain unverified; the cephadm executable is sourced from the
upstream EL9 artifact, a compatibility caveat on Rocky 10.
