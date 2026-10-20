> **Maturity State: Alpha**<br>
> **RC Readiness: 41%**

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
- Cephadm monitor/manager placement, explicitly declared OSD device requests, and declared pool creation (experimental; not production-verified).

The role does not manage:

- Ceph/cephadm package installation, repositories, firewall, time sync, or external PKI.
- Automated device discovery, disk wiping, upgrades/removal, or a verified functioning HA deployment.

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
| install             | Bootstraps the first monitor host, registers declared monitor and OSD hosts, applies monitor/manager and per-device OSD service specs, and creates pools. Repeated application is declarative. |

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
    cluster_name: "ceph"
    monitors: ["ceph-a", "ceph-b", "ceph-c"]
    cluster_network: "10.20.0.0/24"
    osds:
      - { host: "ceph-osd-a", device: "/dev/sdb" }
    pools: []

Top-level blueprint variables
-----------------------------

| Variable          | Required (yes/no) | Default       | Short description           |
|-------------------|-------------------|---------------|-----------------------------|
| cluster_name      | yes               | none          | Cluster name; currently only `ceph` is supported. |
| monitors          | yes               | none          | Odd-sized list of >=3 inventory hosts; the first host is the designated bootstrap host and must be the only host targeted by install. |
| cluster_network   | install            | none          | Explicit private cluster CIDR; required for bootstrap. |
| osds              | no                | []            | Explicit host/device records. A device path must be unique per host; the same path on different hosts is valid. Omitted records do not remove existing OSDs. Hosts are registered from this declaration, so OSD-only inventory hosts are supported. |
| allow_osd_provisioning | no          | false         | Explicitly permits submission of declared device requests to Ceph's orchestrator. Must be boolean `true` when `osds` is non-empty. It does not establish that disks are safe to use. |
| pools             | no                | []            | Pools to create, with optional pg_num (default 32). |

Configuration examples
----------------------

**This role is not production-ready.** OSD provisioning is disabled by default. To submit requests, set `allow_osd_provisioning: true` and explicitly declare OSD host/device records; otherwise validation rejects any non-empty `osds` list before host mutation. This opt-in is only authorization to submit documented Ceph OSD service specs (`data_devices.paths`) using `ceph orch apply -i`; it does **not** prove a device is safe, unused, or intended for Ceph. Review every host and device independently with `ceph orch device ls` and verify ownership/backups before enabling. Ceph's availability checks are not a disk-safety guarantee, and this role does not wipe devices.

Every OSD host must also be present in Ansible inventory. Such hosts may be OSD-only and need not appear in `monitors`; the role registers the union of monitor and declared OSD hosts with the orchestrator. OSD specifications omitted from a later blueprint are not automatically removed; removal must be managed explicitly through Ceph.

Only use install in a disposable, reviewed environment after testing cephadm behavior manually. Target only the first host in `monitors` when invoking install; the role rejects install on any other host to avoid multiple hosts independently attempting bootstrap. Bootstrap only runs when `/etc/ceph/ceph.conf` is absent. Monitor and manager placement and OSD device requests submit declarative orchestrator service specs on every install run. Because Ceph does not expose a stable, directly comparable current spec through this role's CLI workflow, these apply commands report `changed: false`; Ansible changed reporting therefore does not indicate whether Ceph updated a spec. Host registration and pool creation report changes when they issue commands; only bootstrap and pool existence have local guards. A mock CLI test exercises command construction and the local rerun path, not Ceph convergence or idempotence. Ceph's asynchronous orchestration completion and recovery after partial application remain outside role verification. `monitors` validation establishes declared topology only; it does not establish quorum or high availability. Do not use for production clusters. See [the maturity roadmap](docs/ROADMAP.md) for evidence gates.
