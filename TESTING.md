# Testing

This Alpha release has a validation scenario and a mock-CLI install scenario.
Previously recorded scenario results predate the current version/preflight changes; they have not yet been run. The mock scenario checks
command arguments/spec generation, bootstrap's local guard, accepted/rejected
OSD device inventory (including duplicate ambiguous records) and two install passes in one converge play without a Ceph cluster. Mock state and the overridden bootstrap sentinel are confined to `/tmp/ceph-mock-state` in the unmounted Podman container. The
scenario deliberately omits Molecule's separate idempotence phase: its second
install pass is the explicit repeat-install check, using persisted mock host
registration and pool state. It does not verify Ceph
acceptance/convergence, disk safety, OSD provisioning, HA, or platform support.

| Platform/image | Ansible or application versions | Molecule scenarios | Main coverage |
|---|---|---|---|
| Rocky Linux 9 Podman container | Ansible Core >=2.19 | validation — passed | Accepted and rejected blueprint inputs; validation-only non-mutation |
| Rocky Linux 9 Podman container | Ansible Core >=2.19 | install-mock — pending | Installed cephadm version check, pool conflict preflight ahead of mutation, accepted and duplicate-ambiguous/rejected OSD inventory, pinned image and repeated install |

Use the pre-existing shared `idarsi-ansible-test-environments` environment; follow that repository's setup instructions to activate it.

Commands: `molecule test -s validation`; `molecule test -s install-mock`; `ansible-lint --profile production`; `ansible-playbook --syntax-check -i docs/inventory-minimal.yml docs/playbook-example.yml`.

The passing scenarios establish validation behavior and mock command/spec construction plus the local repeat-install path only. The repeated mock pass is not true Ceph idempotence evidence: service specs are submitted each time and reported `changed: false` because the role has no reliable state comparison. Host registration and pool create behavior also need validation against real CLI responses. These tests do not prove live cluster HA, OSD/device safety, Ceph acceptance or convergence, or supported Rocky 9 operation. Live Ceph/cluster execution evidence is still missing; the two passing test scenarios above are scenario-level evidence only. Real multi-host KVM and production-like cluster, recovery, platform matrix and actual idempotence testing remain release blockers. Podman backend is expected; Docker is not supported. See [ROADMAP.md](docs/ROADMAP.md).

The updated scenarios have not been executed for this revision; do not treat
their pending rows as passed. `.github/workflows/quick.yml` defines PR/push checks
for validation, mocked install, production lint, and example syntax. It has not
yet run in GitHub Actions. Rocky 9 and Rocky 10 are intended test-matrix
platforms only; no live/platform support claim is made for either.
