> **Maturity State: Experimental**<br>
> **RC Readiness: 18%**

ANSIBLE-IAC-ROLE-CEPH
===============================
**COPYRIGHT** ^(ida|arsi)$ collective
**LICENSE** MIT Licence [LICENSE](LICENSE)
**AUTHORS**
- Arsi Atomi <arsi@atomi.sh>

Overview
--------

This Ansible role provides a declarative way to validate Ceph cluster topology and perform a limited cephadm bootstrap workflow.

This role uses the `iac_blueprint` model to define the desired state, while
Ansible handles the host-specific implementation. See [Idarsi](https://github.com/idarsi)
for further information.

The role manages:

- Ceph cluster bootstrap and monitor-host registration (experimental).
- Creation of declared pools on the bootstrap host.

The role does not manage:

- Ceph/cephadm package installation, repositories, firewall, time sync, or external PKI.
- OSD provisioning, disk wiping, upgrades, removal, monitor daemon placement, or a verified functioning HA deployment.

Supported platforms
-------------------

| Operating system                  | Supported versions                | Automated test coverage                   |
|-----------------------------------|-----------------------------------|-------------------------------------------|
| Rocky Linux                       | 9                                 | Validation scenario only (not run here; platform claim not independently established) |

Supported states
----------------

| State               | Behaviour                     |
|---------------------|-------------------------------|
| validate            | Validates blueprint only; makes no target changes. |
| install             | Attempts bootstrap, host registration, and pool creation; does not provision OSDs or establish HA. |

Quick start
-----------

See [the blueprint example](docs/playbook-example.yml) and use `state: "validate"` first.

Requirements
------------

Control node

- Ansible Core 2.19 or newer
- None (uses only ansible.builtin)

Target host

- Rocky Linux 9 with a working cephadm/ceph CLI, network connectivity, sudo/root privileges, and a prepared Ceph-compatible environment. The role platform gate is Rocky 9 only; no platform support has been independently verified.
- Bootstrap host must have `ansible_host`; cluster network must be provided.

Blueprint structure
-------------------

Configuration is read from:

iac_blueprint.ceph

Minimal structure:

iac_blueprint:
  ceph:
    cluster_name: "storage"
    monitors: ["ceph-a", "ceph-b", "ceph-c"]
    cluster_network: "10.20.0.0/24"
    osds: []
    pools: []

Top-level blueprint variables
-----------------------------

| Variable          | Required (yes/no) | Default       | Short description           |
|-------------------|-------------------|---------------|-----------------------------|
| cluster_name      | yes               | none          | Cluster name; currently only `ceph` is supported. |
| monitors          | yes               | none          | Odd-sized list of >=3 inventory hosts including bootstrap host. |
| cluster_network   | install            | none          | Explicit private cluster CIDR; required for bootstrap. |
| osds              | no                | []            | Explicit host/device records; non-empty lists validate but install rejects them because provisioning is not implemented. |
| pools             | no                | []            | Pools to create, with optional pg_num (default 32). |
| allow_osd_device_wipe | no            | false         | Guard setting; does not enable OSD provisioning in this release. |

Configuration examples
----------------------

**Full high-availability deployment, including OSD provisioning, is not implemented.** A non-empty OSD list is validated but install rejects it before making host changes. Do not treat this role as satisfying a full HA-cluster request.

Only use install in a disposable, reviewed environment after testing cephadm behavior manually. Bootstrap only runs when `/etc/ceph/ceph.conf` is absent. This initial implementation does not reconcile monitor daemon placement or offer proven retry/idempotence behavior for cluster operations. `monitors` validation establishes declared topology only; it does not establish quorum or high availability. Do not use for production clusters.
