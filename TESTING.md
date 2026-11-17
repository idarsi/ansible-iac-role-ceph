# Testing

This Beta release has validation and mock-CLI scenarios plus a guarded live
multi-host KVM integration scenario. Historical podman-validation, podman-install-mock,
production-profile lint, example syntax, and the then-current KVM sequence passed
at commit `3706511`; that KVM evidence predates the current CephFS coverage.
At assessed commit `a607c7f63ba2e93761ea94ed03e1025d8bc4fe7d` on
`update/cephfs-support`, podman-validation, podman-install-mock, production-profile lint, and
example syntax passed. The former Rocky 10 Tentacle 20.2.4 `kvm-ceph` custom Molecule sequence passed
all eight actions (create, converge/verify twice, cleanup) using shared
environment HEAD `b6b56db`, Ansible Core 2.20.8, and Molecule 26.8.0. The live
run verified three OSDs, an active MDS, `ceph-common`/`mount.ceph`, persistent
mounts across all three clients, cross-node write/read, second convergence with
`changed=0`, and scoped cleanup. These historical results alone do not establish
general Rocky 10 support or Rocky 9 live-cluster support; subsequent supervised
runs below provide separate, scoped live-cluster evidence for both versions.
The mock scenario checks
command arguments/spec generation, bootstrap's local guard, accepted/rejected
OSD device inventory (including duplicate ambiguous records), bootstrap SSH-user arguments, and public-key installation for declared peers, and two install passes in one converge play without a Ceph cluster. Mock state and the overridden bootstrap sentinel are confined to `/tmp/ceph-mock-state` in the unmounted Podman container. The
scenario deliberately omits Molecule's separate idempotence phase: its second
install pass is the explicit repeat-install check, using persisted mock host
registration and pool state. It does not verify Ceph
acceptance/convergence, disk safety, OSD provisioning, HA, or platform support.

| Platform/image | Ansible or application versions | Molecule scenarios | Main coverage |
|---|---|---|---|
| Rocky Linux 9 Podman container | Ansible Core >=2.19 | podman-validation — passed under its former scenario name at 3706511 and `a607c7f` | Accepted and rejected blueprint inputs; validation-only non-mutation. Container validation is not Rocky 9 live-platform evidence. |
| Rocky Linux 10 / Python 3.12 Podman container | Ansible Core >=2.19 | podman-install-mock — passed under its former scenario name at 3706511 and `a607c7f` | Installed cephadm version check, prerequisite package task (container mock skips chronyd), pool conflict preflight, accepted/rejected OSD inventory, duplicate/count and identity cases, pinned image and repeated mocked install; not platform support evidence. |
| Rocky Linux 10 KVM guests (three-node cluster) | Ceph Tentacle 20.2.4; Ansible Core 2.20.8; Molecule 26.8.0 | kvm-ceph — full eight-action CephFS sequence passed at assessed commit `a607c7f` | Three monitors, active and standby manager, three scenario-owned OSDs up/in, pool (`pg_num: 32`, matching the autoscaler-adjusted value observed by KVM diagnostics), non-error health, CephFS with active MDS, `ceph-common` and `mount.ceph` on all three clients, persistent mounts on all nodes, cross-node write/read, second convergence with `changed=0`, and scoped cleanup. |
| Rocky Linux 9 KVM guests (three-node cluster) | Ceph Tentacle 20.2.4; Ansible Core 2.20.8; Molecule 26.8.0; private ansible.posix 2.1.0 | kvm-ceph — supervised sequence passed and cleaned, run `613a2ea1-8486-46a4-aeef-f1da535a4de0` | Three monitors, three OSDs up/in, manager, CephFS and persistent cross-node client mounts; controlled host-add failure recovered; idempotence changed=0 on all three guests; scoped supervisor cleanup. |
| Rocky Linux 10 KVM guests (three-node cluster) | Ceph Tentacle 20.2.4; Ansible Core 2.20.8; Molecule 26.8.0; private ansible.posix 2.1.0 | kvm-ceph — supervised sequence passed and cleaned, run `ba66c9ce-be15-42a5-b151-fee0b135a66d` | Same managed recovery, cluster, CephFS, cross-node mount, idempotence and cleanup checks as the Rocky 9 run. |

Both supervised runs used the existing `ansible-current` environment. Each
provisioned three guests with Kickstart `ignoredisk`/`clearpart` constrained to
the serial-qualified `virtio-itr-root` disk. Each guest's owned `itr-osd1`
data disk resolved to `/dev/vdb`, and that path matched Ceph device inventory.
The injected `ceph-b` host-add failure was caught and retried successfully;
the subsequent idempotence pass reported `changed=0` on all three guests.
Verification confirmed three monitors, three OSDs up/in, manager, CephFS,
persistent client mounts and cross-node access. The supervisor cleaned each
run with zero owned guest/network records remaining; Rocky 10 also had empty
`virsh` guest and network listings. The official HTTPS ISO hashes matched
their checksum files, but the checksum files were not signature-verified.
Two older pre-policy resources remain retained outside these runs.

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

The podman-install-mock scenario checks the exact `ceph fs volume create <name>` CLI
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
The podman-install-mock scenario exercises protocol-aware monitor normalization:
dual-stack and mixed-capability monitor sets select only v2 with `prefer-secure`,
while v1-only sets fall back to `legacy`. The podman-validation scenario covers the
CephFS blueprint's MDS count, client host, filesystem
reference, client identity, accepted `/srv/...` and `/mnt/...` mountpoints, and
rejected root/system-tree, traversal, empty-component, and unsafe-character
forms. During install, each client mountpoint is resolved with `realpath -m`
before package, directory, or mount changes; changed resolutions (including
symlink ancestors) are rejected.

Use the pre-existing shared `idarsi-ansible-test-environments` environment; follow that repository's setup instructions to activate it.

The `podman-install-mock` and `kvm-ceph` scenarios declare the pinned
`ansible.posix` 2.1.0 collection in their own `molecule/*/requirements.yml`.
The KVM scenario's shell dependency invokes its fixed executable
`molecule/kvm-ceph/install-collections`. It first verifies a supervised run
ID, its private run manifest, and the exact trusted ephemeral directory,
including ownership/modes and absence of symlinks. After authorization it
creates the private collections directory and rejects nested links, foreign
inodes and unsafe directory modes before invoking
`ansible-galaxy collection install -r molecule/kvm-ceph/requirements.yml`
with `--collections-path` pointing into that run and `--force`; it never
invokes Galaxy's role installer. The wrapper prepends the private path to
Galaxy's inherited collection search path; the provisioner separately
prepends it for Ansible, so a shared venv collection cannot shadow it.
A direct Molecule invocation
without a matching supervisor journal fails before Galaxy can write.
The KVM converge preflight checks that Ansible's first collection directory
is this run's private path and that its collection manifest is version 2.1.0;
cheap config checks alone did not exercise Galaxy installation or runtime
collection resolution, but both supervised runs used the effective private
`ansible.posix` 2.1.0 collection.
`ansible-min` Core 2.15 is below this role's 2.19 minimum. Do not install
into the shared environment from this role.
The TUI opts only `kvm-ceph` into the managed runner; Podman scenarios still
use direct Molecule. Its Core 2.19 minimum matches `meta/main.yml`. In one
Rocky 10 ISO TUI run (PARTIAL, exit 0), `ansible-min` Core 2.15 was SKIPPED
without starting a runner, not passed or failed. `ansible-current` Core 2.20.8
PASSED (run `267300fe-1e93-4f91-85b3-53ec0d670b93`); `ansible-next`
Core 2.21.3 PASSED (run `121a619f-cb72-4dd3-b304-b3c081927a5a`). Both
managed runs verified the private `ansible.posix` 2.1.0 pin, injected recovery,
CephFS cross-node access, and idempotence with `changed=0` on all three hosts.
Both cleaned with zero owned guest/network records in their manifests; this
does not establish that unrelated host resources are absent.

The live KVM scenario is deliberately excluded from PR/push CI. It is a
manual/scheduled heavy test requiring libvirt/KVM, an available Rocky Linux ISO,
and disposable storage. The managed supervisor in shared test-environments
main `96d6c57` passed the earlier supervised Rocky 9 and Rocky 10 runs;
broader runtime acceptance remains open. After
activating a compatible existing pinned environment, run from the role checkout
with a reviewed Rocky 10 ISO:

```bash
export IDARSI_TEST_KVM_INSTALL_SOURCE=/path/to/Rocky-10-x86_64-dvd.iso
/path/to/idarsi-ansible-test-environments/scripts/test-run run --backend kvm --scenario kvm-ceph
```

The supervisor allocates a private network and disjoint /24, maps stable
logical hostnames to per-run SSH addresses, journals guests/disks and removes
only owned resources after the worker session has stopped. Both Molecule
destroy actions only clear disposable inventory state; final resource cleanup
is outside Molecule. Failed or interrupted runs retain their journal/lease if
cleanup cannot be proved safe; follow shared `docs/isolated-test-runs.md` for
explicit inspection and recovery. Do not invoke direct `molecule test -s kvm-ceph`
without the managed supervisor; direct Podman scenario commands above remain
allowed. Do not manually delete retained old guests or pre-policy failed-run
resources.
The scenario checks all three generated guest addresses share one private /24
and match the supervisor's own run manifest before bootstrap, then derives
`cluster_network` from that validated subnet. Before
bootstrap or host registration, it installs Podman, LVM2, chrony, and
Python 3 on every unique declared monitor/OSD host, then enables/starts chronyd
on systemd hosts. Undeclared inventory hosts are not targeted.
The scenario replaces Ansible's SSH arguments to disable multiplexing and
ignore user SSH configuration (`-F /dev/null`); generated per-guest identity
files remain in use. The provisioner also sets `ANSIBLE_SSH_ARGS` so an inherited
controller environment cannot restore multiplexing.
The scenario's Kickstart limits `clearpart` to the same serial-qualified root
disk as the managed adapter's injected `ignoredisk --only-use` directive,
so no data disk is an installation target. Both supervised ISO installs
passed this root-only guard; no signed ISO authenticity claim is made. The shared adapter
creates one owned 20 GiB qcow2 data disk per guest with
serial `itr-osd1`. Each guest resolves `/dev/disk/by-id/virtio-itr-osd1`,
checks its block device and serial, and passes the resulting kernel device
path to the unchanged role blueprint. The resolved path (expected `/dev/vdX`,
not assumed to be `/dev/vdb`) must match Ceph's reported device path on the
live guest. The role additionally requires Ceph
orchestrator inventory to contain that exact path and establish availability
or matching role ownership before submitting an OSD specification.
The CephFS cross-node probe contains a fresh opaque random token, not a
controller filesystem path.
Recovery injects only the exact `ceph-b` host-add command via a securely created
temporary `PATH` directory. It checks the failed loop result's `cmd` and exit
code, rejects additional/unexpected failures and missing injection, then retries
with the normal `PATH` and unchanged valid blueprint. Only successful retry
writes a guest-local completion marker; subsequent convergence skips injection
and runs the normal role. The owned temporary directory is always removed;
host `cephadm` binaries are never overwritten or deleted. Both supervised
runs passed this controlled recovery and repeat-convergence sequence. Never
run it against valuable VMs or storage. For Rocky 9, run the same supervised
command after setting `IDARSI_TEST_KVM_INSTALL_SOURCE` to a reviewed Rocky 9
ISO. Run Rocky 9 and Rocky 10 sequentially; one invocation selects one ISO.
The default full
Molecule sequence includes dependency, initial and final destroy, convergence,
idempotence (a second converge), and verify. The first converge injects one
controlled failure and retries; the idempotence converge skips injection.
Both recorded managed runs passed and cleaned; this does not prove recovery
from arbitrary failures or safe cleanup outside their owned resources.

Commands: `molecule test -s podman-validation`; `molecule test -s podman-install-mock`; `ansible-lint --profile production`; `ansible-playbook --syntax-check -i docs/inventory-minimal.yml docs/playbook-example.yml`.
The example syntax check passed after adding the explicit OSD opt-in to the
validation-only playbook. The linked example also passed local validation-only
execution with `ansible-playbook -i docs/inventory-minimal.yml
docs/playbook-example.yml --limit ceph-a -e 'ansible_connection=local'
-e '{"ansible_facts":{"distribution":"Rocky","distribution_major_version":"9"}}'`:
`ok=20`, `changed=0`, `unreachable=0`, `failed=0`, `skipped=4`; install was
skipped and no documentation addresses were contacted. Syntax checking alone
does not run blueprint validation.

The historical KVM evidence applies to the former custom sequence and
name-based lifecycle, not the current managed supervisor. The newer supervised
runs establish controlled host-add failure/retry, repeat convergence and scoped
cleanup on Rocky 9 and 10; neither sequence proves arbitrary failure recovery,
upgrade/removal, or accurate changed reporting for MON/MGR/OSD specs. Repeated
specs may report `changed: false` without reliable state comparison. MDS
reconciliation uses placement-count matching, not general cluster-state
comparison. The tests do not prove physical-device safety or production
readiness. Shared GitHub CI enforcement has not been established. Upgrade/
removal, MON/MGR/OSD changed reporting, broader platform/dependency coverage,
and production-like evidence remain gaps. Podman backend is expected; Docker
is not supported. See [ROADMAP.md](docs/ROADMAP.md).

The prior Rocky 9 / Python 3.9 podman-install-mock incompatibility was addressed by
running the mock on Rocky 10 / Python 3.12. At 3706511, configured
validation, mock, lint, and syntax checks passed locally; the same focused
checks passed at assessed commit `a607c7f`. `.github/workflows/quick.yml`
defines PR/push checks, but successful shared GitHub Actions enforcement has
not been established. Rocky 9 and 10 have scoped live-cluster evidence, not
general platform certification; the cephadm executable is sourced from the
upstream EL9 artifact, a compatibility caveat on Rocky 10.
