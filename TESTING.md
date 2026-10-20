# Testing

This experimental release has one validation-only Molecule scenario. It is not evidence of cluster installation or platform support.

| Platform/image | Ansible or application versions | Molecule scenarios | Main coverage |
|---|---|---|---|
| Rocky Linux 9 container | Ansible Core >=2.19 (not executed) | validation | Accepted input and no Ceph config mutation |

Use the pre-existing shared environment: `source /home/arsi/jeps/idarsi-ansible-test-environments/.venv/ansible-current/bin/activate`.

Commands: `molecule test -s validation`; `ansible-lint --profile production`; `ansible-playbook --syntax-check -i docs/inventory-minimal.yml docs/playbook-example.yml`.

The developer did not run Molecule. Full cluster, OSD safety, pool, idempotence, and RHEL testing remain unimplemented and are release blockers. Podman backend is expected; Docker is not supported.
