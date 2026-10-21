> **Maturity State: Beta**<br>
> **RC Readiness: 73% (floor)**
> **Assessment ref:** commit [`3706511`](https://github.com/idarsi/ansible-iac-role-ceph/commit/3706511)

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

- Firewall or external PKI.
- Automated device discovery, disk wiping, upgrades/removal, or a verified functioning HA deployment.

Supported platforms
-------------------

| Operating system                  | Supported versions                | Automated test coverage                   |
|-----------------------------------|-----------------------------------|-------------------------------------------|
| Rocky Linux                       | 9, 10 (role platform gate)        | Rocky 9 validation container only; live cluster and support unverified. Rocky 10 install-mock container and Tentacle 20.2.4 KVM integration sequence passed; this is not general support evidence. |

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
- `ansible.posix` collection (pinned to `2.1.0` by the Molecule scenarios; install it on the control node for role use)

Target host

- Rocky Linux 9 or 10 with network connectivity and sudo/root privileges. On the bootstrap host, install converges Podman, LVM2, Chrony, Python 3, and the official pinned Tentacle 20.2.4 cephadm executable (download.ceph.com RPM release path for EL9). Rocky 10 compatibility of that upstream EL9 cephadm binary remains unverified.
- Bootstrap pins the daemon container to `quay.io/ceph/ceph:v20.2.4` (Tentacle), installed cephadm must report a parseable version with major version 20 or newer and matching major version 20.
- Bootstrap host must have `ansible_host`; cluster network must be provided.
- The role passes `ceph.ssh_user` to bootstrap (default: `root`), then installs only the Ceph bootstrap public key (`/etc/ceph/ceph.pub`) for that account on declared monitor and OSD hosts before host registration. The account must have passwordless sudo on each peer; non-root users are supported. The role never reads or distributes the private key.

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
| ssh_user          | no                | `root`        | Pre-existing SSH account Ceph uses to manage declared peers; must have passwordless sudo. |
| osds              | no                | []            | Explicit host/device records. A device path must be unique per host; the same path on different hosts is valid. Omitted records do not remove existing OSDs. Hosts are registered from this declaration, so OSD-only inventory hosts are supported. |
| allow_osd_provisioning | no          | false         | Explicitly permits submission of declared device requests to Ceph's orchestrator. Must be boolean `true` when `osds` is non-empty. It does not establish that disks are safe to use. |
| pools             | no                | []            | Pools to create, with optional pg_num (default 32). |

Configuration examples
----------------------

**This role is not production-ready.** OSD provisioning is disabled by default. To submit requests, set `allow_osd_provisioning: true` and explicitly declare OSD host/device records; otherwise validation rejects any non-empty `osds` list before host mutation. This opt-in is only authorization to submit documented Ceph OSD service specs (`data_devices.paths`) using `ceph orch apply -i`; it does **not** prove a device is safe, unused, or intended for Ceph. Review every host and device independently with `ceph orch device ls` and verify ownership/backups before enabling. Ceph's availability checks are not a disk-safety guarantee, and this role does not wipe devices.

Every OSD host must also be present in Ansible inventory. Such hosts may be OSD-only and need not appear in `monitors`; the role registers the union of monitor and declared OSD hosts with the orchestrator. OSD specifications omitted from a later blueprint are not automatically removed; removal must be managed explicitly through Ceph.

Only use install in a disposable, reviewed environment after testing cephadm behavior manually. Target only the first host in `monitors`; bootstrap is guarded by `/etc/ceph/ceph.conf`. Bootstrap necessarily precedes the live existing-pool `pg_num` check because that check requires Ceph CLI access; consequently a pool conflict on a clean host can fail after the cluster has been bootstrapped. Pool conflicts fail rather than being changed. The role then registers monitor/OSD hosts, waits (up to 60 seconds) for registration, and checks orchestrator device inventory before applying any monitor, manager, or OSD daemon specs. Host registration intentionally precedes device inventory because newly registered OSD hosts must be visible to `ceph orch device ls`; therefore a rejected device can leave those hosts registered, but no daemon/OSD specs are applied. The inventory check is a fail-closed snapshot advisory only: inventory can change immediately after it is read (TOCTOU), it does not guarantee device safety, and it does not wipe devices. Specifications report `changed: false`, not actual cluster change state. In the Rocky 10 Tentacle 20.2.4 KVM scenario, the observed three-monitor quorum and active-plus-standby manager checks passed. Sustained HA, failover, and recovery (including recovery after partial application) remain unverified. Do not use for production clusters. See [the maturity roadmap](docs/ROADMAP.md) for evidence gates.
