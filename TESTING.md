# Testing

This Alpha release has a validation scenario and a mock-CLI install scenario.
The mock scenario checks command arguments/spec generation, bootstrap's local
guard, and two install passes without a Ceph cluster. It does not verify Ceph
acceptance/convergence, disk safety, OSD provisioning, HA, or platform support.

| Platform/image | Ansible or application versions | Molecule scenarios | Main coverage |
|---|---|---|---|
| Rocky Linux 9 container | Ansible Core >=2.19 (not executed here) | validation | Accepted and rejected blueprint inputs; validation-only non-mutation |
| Rocky Linux 9 container | Ansible Core >=2.19 (not executed here) | install-mock | Stubbed cephadm/ceph arguments, monitor/manager spec generation, bootstrap guard, repeated install command behavior |

Use the pre-existing shared environment: `source /home/arsi/jeps/idarsi-ansible-test-environments/.venv/ansible-current/bin/activate`.

Commands: `molecule test -s validation`; `molecule test -s install-mock`; `ansible-lint --profile production`; `ansible-playbook --syntax-check -i docs/inventory-minimal.yml docs/playbook-example.yml`.

The developer did not run Molecule. The repeated mock pass is not real Ceph idempotence evidence: service specs are submitted each time and reported `changed: false` because the role has no reliable state comparison. Host registration and pool create behavior also need validation against real CLI responses. Real multi-host KVM and production-like cluster, OSD safety, pool, recovery, platform matrix and actual idempotence testing remain release blockers. Podman backend is expected; Docker is not supported. See [ROADMAP.md](docs/ROADMAP.md).
