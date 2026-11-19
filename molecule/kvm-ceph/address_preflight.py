"""Validate the cluster addresses against an already validated context subnet."""

import ipaddress


def validated_network(addresses: list[str], allocated_subnet: str) -> str:
    """Require three unique private IPv4 hosts in the allocated /24."""
    network = ipaddress.ip_network(allocated_subnet, strict=True)
    guests = [ipaddress.ip_address(value) for value in addresses]
    if (network.version != 4 or network.prefixlen != 24 or not network.is_private
            or len(guests) != 3 or len(set(guests)) != 3
            or any(address.version != 4 or not address.is_private
                   or address not in network
                   or address in (network.network_address, network.broadcast_address)
                   for address in guests)):
        raise ValueError("Ceph guests need three distinct private hosts in the allocated /24")
    return str(network)
