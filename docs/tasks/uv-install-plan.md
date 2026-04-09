# uv-Based Installation for bashhub

## Context

The current install script bootstraps a custom Python virtualenv at `~/.bashhub/env/`, installs bashhub into it, and symlinks `bh`/`bashhub` into `~/.bashhub/bin/`. This requires a compatible Python (3.9–3.14) to already be on the system.

The question is: what would replacing this with `uv tool install` look like, and what are the tradeoffs?

---

## What Would Change

### install-bashhub.sh — Dramatically simplified

The bulk of the script (virtualenv bootstrap, tarball download, pip install, symlinking) collapses into roughly:

```bash
# 1. Install uv (single binary, no Python required)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install bashhub (uv downloads Python automatically)
uv tool install git+https://github.com/rcaloras/bashhub-client@3.0.2

# 3. Run first-time setup (same as today)
bashhub setup
```

That's it. `check_dependencies`, `download_and_install_env`, the entire virtualenv section, and the symlink wiring all go away.

### Shell hooks — Minor PATH change

The hooks currently do:
```bash
__bh_path_add "$HOME/.bashhub/bin"   # current
```

With uv, binaries land at `~/.local/bin` (on Linux/macOS). This is typically already on PATH, so this line may not even be needed. But to be safe, it becomes:
```bash
__bh_path_add "$HOME/.local/bin"     # uv tool default
```
The hooks already call `bashhub` by name (not hardcoded paths), so nothing else changes there.

### Config/data directory — Unchanged
`~/.bashhub/config`, shell deps, and all user data stay at `~/.bashhub/`. Only the binary location moves.

### setup.py / packaging — Unchanged for now
`uv tool install` works from a GitHub URL today without PyPI. Publishing to PyPI (Phase 2 of the distribution plan) would make it even cleaner (`uv tool install bashhub`) but isn't required for this step.

### Upgrades — Much better UX
```bash
uv tool upgrade bashhub   # vs. re-running the install script
```

---

## Tradeoffs

### File size & disk footprint

| Approach | What's on disk | Approx size |
|---|---|---|
| Current custom venv | `~/.bashhub/env/` (venv) | ~80–120 MB |
| `uv tool install` | `~/.local/share/uv/tools/bashhub/` (venv) + uv-managed Python | ~100–150 MB |
| PyInstaller binary | Single self-contained executable | ~30–60 MB |

**uv is not smaller than the current approach** — it still creates an isolated venv and downloads a Python runtime. The key advantage is that uv's Python download is shared across all uv-managed tools (global cache at `~/.cache/uv`), so the cost amortizes if users already use uv for other things.

### Portability

| | Current | uv tool | PyInstaller |
|---|---|---|---|
| Requires system Python | Yes (3.9–3.14) | No — uv downloads Python | No — bundled |
| Requires uv | No | Yes (~15 MB binary) | No |
| Works offline | No (downloads at install) | No (downloads at install) | Yes (after download) |
| Cross-platform | Manual per-platform | Yes, automatic | Requires per-platform build |
| Update mechanism | Re-run install script | `uv tool upgrade bashhub` | Re-download binary |

**uv solves the system Python problem** (the root cause of the 3.14/npyscreen incident) but trades it for a dependency on uv. uv itself is a single static binary ~15 MB — much lighter than requiring a specific Python version.

**PyInstaller is the most portable** (single file, nothing required) but requires a per-platform build pipeline and produces a larger binary.

### Recommendation

`uv tool install` is the right next step:
- Eliminates the system Python dependency
- Minimal changes to the existing codebase
- Works from GitHub without PyPI (no new release infrastructure needed)
- Clean upgrade path for users
- Can be done before PyPI publishing

PyInstaller is a longer-term option worth revisiting after PyPI publishing is in place, as the build pipeline complexity is more justified once there's proper release automation.

---

## Files to Change

- `install-bashhub.sh` — replace virtualenv bootstrap + pip install with uv install
- `bashhub/shell/bashhub.sh` — update `__bh_path_add` target (line ~27 in lib-bashhub.sh)
- `bashhub/shell/bashhub.zsh` — same
- `bashhub/shell/bashhub.fish` — same
- `docs/tasks/distribution-plan.md` — this is tracked under Phase 2

## Verification

1. Fresh install on a machine without Python — verify `bh` and `bashhub` are available
2. Run `bashhub setup` through the new install flow
3. Run `uv tool upgrade bashhub` and verify it works
4. Verify shell hooks still capture and save commands correctly
5. Run existing test suite: `pytest tests/`
