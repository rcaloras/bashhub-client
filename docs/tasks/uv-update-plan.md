# UV-Based Bashhub Updates

## Summary

Bashhub updates should use UV for the Python runtime, package environment, and executable shims. The Bashhub installer remains responsible for Bashhub-specific setup: shell integration, config preservation, setup repair, and local file permissions.

## Update Model

- Latest updates use `uv tool upgrade bashhub`.
- Version-specific updates and rollbacks use `uv tool install --python 3.13 --reinstall "bashhub==<version>"`.
- Re-running `install-bashhub.sh` is an idempotent install, update, and repair flow.
- `bashhub update` remains the user-facing command, but delegates to the hosted installer so all install/update/repair paths share the same Bash logic.

## Installer Responsibilities

- Preserve `~/.bashhub/config` before touching install files.
- Ensure UV is installed.
- Install Bashhub with `uv tool install --python 3.13 bashhub` if missing.
- Upgrade Bashhub with `uv tool upgrade bashhub` if already UV-managed.
- Copy packaged shell files from the installed package into `~/.bashhub`.
- Reinstall shell profile hooks idempotently.
- Run `bashhub util update-system-info`, falling back to `bashhub setup` on failure.

## Intended UX

Latest update:

```bash
bashhub update
```

Equivalent package update:

```bash
uv tool upgrade bashhub
bashhub util update-system-info || bashhub setup
```

Version-specific update:

```bash
bashhub update 3.0.4
```

Equivalent package update:

```bash
uv tool install --python 3.13 --reinstall "bashhub==3.0.4"
bashhub util update-system-info || bashhub setup
```

Repair or reinstall:

```bash
curl https://bashhub.com/setup | bash
```

The installer should safely converge the local machine to the desired state without requiring users to know whether they are installing, updating, or repairing.

## Assumptions

- Bashhub is published to PyPI as `bashhub`.
- UV is the primary supported install and update mechanism.
- `pipx` can be documented as an alternate manual path, but is not an automatic installer fallback.
