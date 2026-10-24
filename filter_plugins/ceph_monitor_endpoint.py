"""Validation helpers for Ceph monitor endpoint strings."""

import ipaddress
import re

def ceph_monitor_endpoint(value):
    """Return whether value is a canonical IP address and valid port pair."""
    if not isinstance(value, str):
        return False

    ipv4 = re.fullmatch(r"([^:\[\]]+):([0-9]+)", value)
    ipv6 = re.fullmatch(r"\[([^\[\]]+)\]:([0-9]+)", value)
    match = ipv4 or ipv6
    if match is None:
        return False

    address, port_text = match.groups()
    try:
        parsed = ipaddress.ip_address(address)
        port = int(port_text)
    except ValueError:
        return False

    return parsed.version == (4 if ipv4 else 6) and 1 <= port <= 65535


def ceph_mds_is_active(value, filesystem):
    """Return whether ceph mds stat reports an active rank for filesystem."""
    if not isinstance(value, str) or not isinstance(filesystem, str) or not filesystem:
        return False

    section_pattern = re.compile(
        rf"(?<!\S){re.escape(filesystem)}:(\d+)\s+\{{([^{{}}]*)\}}"
    )
    for line in value.splitlines():
        for match in section_pattern.finditer(line):
            for rank in match.group(2).split(","):
                _, separator, daemon_status = rank.partition("=")
                if separator and daemon_status.endswith("=up:active"):
                    return True
    return False


class FilterModule:
    """Expose monitor endpoint validation to Ansible."""

    def filters(self):
        return {
            "ceph_monitor_endpoint": ceph_monitor_endpoint,
            "ceph_mds_is_active": ceph_mds_is_active,
        }
