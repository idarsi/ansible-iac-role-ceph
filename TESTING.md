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
| Rocky Linux 10 KVM guests (three-node cluster) | Python 3.12.16; Ansible Core 2.20.8; Molecule 26.8.0; private ansible.posix 2.1.0 | kvm-ceph — plain direct full sequence passed on 2026-11-19 at `update/portable-molecule-testing` working tree | Private collection preservation across initial destroy/pruning, controlled host-add rescue/retry, zero-change idempotence on all three hosts, quorum/MGR/OSD/pool/health and CephFS persistent cross-node mount verification, final scoped destroy and zero owned guests/network. |

The current direct acceptance used plain `molecule test -s kvm-ceph` from the
role checkout, with the updated shared helpers selected through
`IDARSI_TEST_ENVIRONMENT` and no outer runner. Dependency installation, initial
destroy, syntax, create, converge, idempotence, verify and final destroy all
passed. Galaxy installed the private `ansible.posix` 2.1.0 collection without
installing into the shared environment. Its manifest remained 2.1.0 after
final pruning; converge's real context/pin/subnet preflight after initial
destroy also established preservation at that boundary.
The controlled host-add failure was rescued and retried, followed by
`changed=0` on all three guests. Verification passed monitor quorum, manager,
OSD/pool/health, active CephFS, persistent client mounts and cross-node access.
Final inspection confirmed zero owned guests/network, sealed create/destroy
operations and no active generation; pre-existing foreign resources remained
present. This is direct Rocky 10/current-controller evidence only, not new
Rocky 9, next-controller or supervised acceptance. Shared supervised-admission
changes remain separately gated; they do not invalidate or require repeating
this completed direct cluster run.

Both historical supervised runs used the existing `ansible-current` environment. Each
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
`molecule/kvm-ceph/install-collections`. It uses the shared validated context
helper before Galaxy writes, including for direct Molecule commands. Collections
are installed into the actual Molecule ephemeral directory, not the activated
environment or a hard-coded venv layout. The installer rejects nested links,
foreign inodes and unsafe directory modes and serializes its private writes.
It invokes only
`ansible-galaxy collection install -r molecule/kvm-ceph/requirements.yml`
with `--collections-path` pointing into that context and `--force`, never the
role installer. The private collection path precedes inherited paths for both
Galaxy and Ansible so a shared collection cannot shadow it.
Converge checks that Ansible's first collection directory is this context's
private path and its collection manifest is version 2.1.0.
The historical supervised runs used the effective private `ansible.posix`
2.1.0 collection; those runs do not validate the new context integration.
The 2026-11-19 direct run above provides that separate scoped evidence.
`ansible-min` Core 2.15 is below this role's 2.19 minimum. Do not install
into the shared environment from this role.
Additional historical Rocky 10 ISO supervised runs passed under
`ansible-current` Core 2.20.8 (run
`267300fe-1e93-4f91-85b3-53ec0d670b93`) and `ansible-next` Core 2.21.3
(run `121a619f-cb72-4dd3-b304-b3c081927a5a`). The Core 2.15 lane was
skipped as unsupported, not passed or failed. Both managed runs verified the
private `ansible.posix` 2.1.0 pin, injected recovery,
CephFS cross-node access, and idempotence with `changed=0` on all three hosts.
Both cleaned with zero owned guest/network records in their manifests; this
does not establish that unrelated host resources are absent.

The live KVM scenario is deliberately excluded from PR/push CI. It is a manual
heavy test requiring libvirt/KVM, an available Rocky Linux ISO, at least 18 GiB
of guest RAM plus host headroom, and disposable storage. A scheduled/release
runner is not configured here. The cluster is one execution unit containing
all three guests; do not split it into per-platform invocations.
The shared tooling's capability preflight must pass before provisioning.
After activating a compatible existing pinned environment, run from the role
checkout with `IDARSI_TEST_ENVIRONMENT` pointing to its shared tooling checkout
and a reviewed Rocky 10 ISO:

```bash
export IDARSI_TEST_KVM_INSTALL_SOURCE=/path/to/Rocky-10-x86_64-dvd.iso
molecule test -s kvm-ceph
```

No external runner is required. To retain guests for diagnosis, use the same
checkout, activated environment and Molecule ephemeral context for each action:

```bash
molecule create -s kvm-ceph
molecule converge -s kvm-ceph
molecule verify -s kvm-ceph
molecule destroy -s kvm-ceph
```

The dependency resolves the effective context without allocating a generation
before the initial destroy in `molecule test`. Creation then allocates the
generation; converge inspects it afresh rather than caching an identifier across
destroy/create. Collection installation remains in the actual ephemeral
directory across the initial destroy. The shared context allocates a private network and disjoint /24,
maps logical hostnames to per-context SSH addresses, journals guests/disks and
removes only owned resources. Direct concurrent commands sharing one context
are unsupported; different contexts must have separate ephemeral directories.
Optional isolated supervision is documented in the shared tooling's
[`docs/isolated-test-runs.md`](https://github.com/idarsi/idarsi-ansible-test-environments/blob/main/docs/isolated-test-runs.md).
An interrupted host mutation is not automatically recoverable: an incomplete
operation retains resources and its lease and permits inspection only until a
supported backend completion barrier proves it safe to proceed. Do not manually
delete retained old guests or pre-policy failed-run resources.
The scenario checks all three generated guest addresses share one private /24
and match the shared validated context's allocated subnet before bootstrap, then derives
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
run it against valuable VMs or storage. For Rocky 9, run the same direct
command after setting `IDARSI_TEST_KVM_INSTALL_SOURCE` to a reviewed Rocky 9
ISO. Run Rocky 9 and Rocky 10 sequentially; one invocation selects one ISO.
The default full
Molecule sequence includes dependency, initial and final destroy, convergence,
idempotence (a second converge), and verify. The first converge injects one
controlled failure and retries; the idempotence converge skips injection.
Both recorded historical managed runs passed and cleaned. The new direct
Rocky 10/current-controller lifecycle also passed on 2026-11-19; new Rocky 9,
next-controller and supervised acceptance remain pending. These successes do
not prove recovery from arbitrary failures or safe cleanup outside owned resources.

Commands: `molecule test -s podman-validation`; `molecule test -s podman-install-mock`; `ansible-lint --profile production`; `ansible-playbook --syntax-check -i docs/inventory-minimal.yml docs/playbook-example.yml`.
The example syntax check passed after adding the explicit OSD opt-in to the
validation-only playbook. The linked example also passed local validation-only
execution with `ansible-playbook -i docs/inventory-minimal.yml
docs/playbook-example.yml --limit ceph-a -e 'ansible_connection=local'
-e '{"ansible_facts":{"distribution":"Rocky","distribution_major_version":"9"}}'`:
`ok=20`, `changed=0`, `unreachable=0`, `failed=0`, `skipped=4`; install was
skipped and no documentation addresses were contacted. Syntax checking alone
does not run blueprint validation.

The historical custom KVM evidence applies to the former custom sequence and
name-based lifecycle, not the new shared context lifecycle. The later supervised
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

## Portable context integration checks (2026-11-19)

Before adding the real-helper smoke below, `update/portable-molecule-testing`
passed 14 fixture-only tests in the existing approved `ansible-current` Python with
`python -m unittest discover -s molecule/kvm-ceph -p 'test_*.py' -v`.
These mock the shared helper and Galaxy boundaries and cover both context
modes, fail-closed handoff forwarding, generation identity, incomplete mutation
rejection before guest convergence, private collection
pin/search order, links/hardlinks/writable entries, exclusive collection locks
and the allocated three-host subnet. They do not provision guests or install
collections. AST parsing of the then-current five scenario Python files, YAML parsing of
changed YAML, and
`ansible-playbook --syntax-check -i 'ceph-a,ceph-b,ceph-c,' molecule/kvm-ceph/converge.yml`
also passed. `git diff --check` passed. Shared tooling was selected with
`IDARSI_TEST_ENVIRONMENT` pointing to its reviewed worktree; no dependencies
were installed or environments changed during these cheap checks. The subsequent
direct Rocky 10/current-controller runtime passed as recorded above; new
Rocky 9, next-controller and supervised acceptance remain pending.

The review follow-up adds
`driver.safe_files: ["${MOLECULE_EPHEMERAL_DIRECTORY}/collections/*"]` so
Molecule's pruning preserves installed collection files across initial destroy.
The real shared-helper config smoke
`python -m unittest discover -s molecule/kvm-ceph -p 'test_real_context_config.py' -v`
passed separately in the existing approved `ansible-min` and `ansible-current`
environments against the reviewed shared tooling worktree. It invokes actual
`resolve` and `capabilities`, verifies generation remains null, and checks the
effective preservation entry against the actual ephemeral path. No backend
discovery/allocation, create, destroy or Galaxy installation was required.
Inspection of both installed Molecule versions confirmed `Scenario.prune`
uses `fnmatch` against `driver.safe_files`; nested collection files match this
entry. This is config/pruning-code evidence, not a completed lifecycle test.
The Core 2.15 config check does not make that controller supported for role
execution. The smoke is skipped when the shared-tooling variable is absent,
as in standalone quick CI; a supplied but invalid variable fails rather than
skipping validation.
