"""Consume the shared validated context without assuming a venv or run layout."""

import json
import os
from pathlib import Path
import stat
import subprocess
import sys

from address_preflight import validated_network


ROLE = Path(__file__).resolve().parents[2]


def owned_directory(path: Path) -> None:
    """Reject links, foreign ownership and group/world-writable directories."""
    info = path.lstat()
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) & 0o022):
        raise ValueError(f"Untrusted context directory: {path}")


def context(action: str, env: dict, role: Path = ROLE) -> dict:
    """Resolve or inspect through the shared helper; never infer authorization."""
    root = env.get("IDARSI_TEST_ENVIRONMENT", "")
    if not root or not Path(root).is_absolute():
        raise ValueError("IDARSI_TEST_ENVIRONMENT must identify the shared tooling checkout")
    if action not in ("resolve", "inspect"):
        raise ValueError("Unsupported context action")
    try:
        completed = subprocess.run(
            [sys.executable, str(Path(root) / "scripts/scenario-context"), action,
             "--backend", "kvm", "--scenario", "kvm-ceph", "--role", str(role.resolve())],
            env=env, check=True, capture_output=True, text=True,
        )
    except subprocess.CalledProcessError as error:
        raise ValueError(f"Shared context validation failed: {error.stderr.strip()}") from error
    result = json.loads(completed.stdout)
    if (not isinstance(result, dict) or result.get("schema") != "idarsi.scenario-context/v1"
            or result.get("mode") not in ("direct", "supervised")
            or result.get("effective_config_validated") is not True
            or result.get("lifecycle_modes") != ["direct", "supervised"]
            or result.get("role") != str(role.resolve())
            or result.get("scenario") != "kvm-ceph" or result.get("backend") != "kvm"):
        raise ValueError("Shared context does not authorize this role and scenario")
    ephemeral = Path(result["ephemeral_directory"])
    if (not ephemeral.is_absolute() or ephemeral == Path("/")
            or ephemeral != ephemeral.resolve()
            or result["collections_directory"] != str(ephemeral / "collections")):
        raise ValueError("Shared context returned an unsafe collection destination")
    owned_directory(ephemeral)
    supplied = env.get("MOLECULE_EPHEMERAL_DIRECTORY")
    if supplied and Path(supplied).resolve() != ephemeral:
        raise ValueError("Shared context differs from Molecule's actual ephemeral directory")
    return result


def check_pin(ephemeral: Path, env: dict) -> None:
    """Verify the effective first collection path and private exact version."""
    private = ephemeral / "collections"
    paths = env.get("ANSIBLE_COLLECTIONS_PATH", "").split(":")
    if not paths[0] or Path(paths[0]) != private:
        raise ValueError("Context collections must precede shared collections")
    directory = private
    owned_directory(directory)
    for component in ("ansible_collections", "ansible", "posix"):
        directory /= component
        owned_directory(directory)
    descriptor = os.open(directory / "MANIFEST.json", os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, encoding="utf-8") as stream:
        info = os.fstat(stream.fileno())
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) & 0o022):
            raise ValueError("Untrusted collection manifest")
        if json.load(stream)["collection_info"]["version"] != "2.1.0":
            raise ValueError("Context requires ansible.posix 2.1.0")


def main(addresses: list[str]) -> int:
    """Inspect the current generation and print only its validated cluster CIDR."""
    try:
        result = context("inspect", dict(os.environ))
        manifest = result["manifest"]
        if (not result["generation"] or manifest["id"] != result["generation"]
                or manifest["role"] != result["role"]
                or manifest["scenario"] != "kvm-ceph" or manifest["backend"] != "kvm"
                or manifest["status"] != "running" or not manifest["network"]):
            raise ValueError("No active allocated Ceph context")
        if any(operation.get("completion") != operation["id"]
               for operation in manifest.get("operations", [])):
            raise ValueError("Incomplete backend mutation: retain resources and lease; inspection only")
        check_pin(Path(result["ephemeral_directory"]), dict(os.environ))
        print(validated_network(addresses, manifest["subnet"]))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"Ceph context preflight: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
