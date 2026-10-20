# Testing

This Alpha release has validation and mock-CLI scenarios plus a guarded live
multi-host KVM integration scenario (not yet run).
Previously recorded scenario results predate the current version/preflight changes; they have not yet been run. The mock scenario checks
command arguments/spec generation, bootstrap's local guard, accepted/rejected
OSD device inventory (including duplicate ambiguous records), bootstrap SSH-user arguments, and public-key installation for declared peers, and two install passes in one converge play without a Ceph cluster. Mock state and the overridden bootstrap sentinel are confined to `/tmp/ceph-mock-state` in the unmounted Podman container. The
scenario deliberately omits Molecule's separate idempotence phase: its second
install pass is the explicit repeat-install check, using persisted mock host
registration and pool state. It does not verify Ceph
acceptance/convergence, disk safety, OSD provisioning, HA, or platform support.

| Platform/image | Ansible or application versions | Molecule scenarios | Main coverage |
|---|---|---|---|
| Rocky Linux 9 Podman container | Ansible Core >=2.19 | validation — passed | Accepted and rejected blueprint inputs; validation-only non-mutation |
| Rocky Linux 9 Podman container | Ansible Core >=2.19 | install-mock — pending | Installed cephadm version check, pool conflict preflight ahead of mutation, accepted and duplicate-ambiguous/rejected OSD inventory, pinned image and repeated install |
| Rocky Linux 9 KVM guests (three-node cluster) | Ceph Tentacle 20.2.4; Ansible Core >=2.19 | kvm-ceph — implemented, not run | Real bootstrap/host registration, 3 monitors, active manager, two scenario-owned OSD disks, pool, non-ERR health, repeat convergence and scoped cleanup |

Use the pre-existing shared `idarsi-ansible-test-environments` environment; follow that repository's setup instructions to activate it.

The `install-mock` and `kvm-ceph` scenarios each install their pinned
`ansible.posix` collection (`molecule/*/requirements.yml`) through Molecule's
Galaxy dependency step; no shared Ansible environment dependency is changed.

The live KVM scenario is deliberately excluded from PR/push CI. It is a
manual/scheduled heavy test requiring libvirt/KVM, an available Rocky 9 ISO,
and disposable storage. After activating `ansible-current` from the shared
environment and confirming the `idarsi-test-bases` storage pool and shared
`idarsi-test` network:

```bash
export IDARSI_TEST_KVM_INSTALL_SOURCE=/path/to/Rocky-9-x86_64-dvd.iso
export IDARSI_CEPH_KVM_DISPOSABLE=YES_I_WILL_DESTROY_THESE_VMS_AND_DISKS
molecule test -s kvm-ceph
```

The exact acknowledgment is required by both create and destroy. The scenario
uses static addresses `.21`–`.23` on the shared NAT network and creates only
two named ephemeral OSD volumes in the active `idarsi-test-bases` pool
(override with `IDARSI_CEPH_OSD_VOLUME_POOL` if needed); it removes those
volumes and the three shared-lifecycle guests at teardown. Never run it against valuable VMs
or storage. Repeat separately with Rocky 10 by setting the install source to
its ISO; Rocky 10 remains unverified and is not claimed as live-supported by
this scenario definition alone.

Commands: `molecule test -s validation`; `molecule test -s install-mock`; `ansible-lint --profile production`; `ansible-playbook --syntax-check -i docs/inventory-minimal.yml docs/playbook-example.yml`.

The passing scenarios establish validation behavior and mock command/spec construction plus the local repeat-install path only. The repeated mock pass is not true Ceph idempotence evidence: service specs are submitted each time and reported `changed: false` because the role has no reliable state comparison. Host registration and pool create behavior also need validation against real CLI responses. These tests do not prove live cluster HA, OSD/device safety, Ceph acceptance or convergence, or supported Rocky 9 operation. Live Ceph/cluster execution evidence is still missing; the two passing test scenarios above are scenario-level evidence only. Real multi-host KVM and production-like cluster, recovery, platform matrix and actual idempotence testing remain release blockers. Podman backend is expected; Docker is not supported. See [ROADMAP.md](docs/ROADMAP.md).

The updated scenarios have not been executed for this revision; do not treat
their pending rows as passed. `.github/workflows/quick.yml` defines PR/push checks
for validation, mocked install, production lint, and example syntax. It has not
yet run in GitHub Actions. Rocky 9 and Rocky 10 are intended test-matrix
platforms only; no live/platform support claim is made for either.
