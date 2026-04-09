# Distribution & Packaging Improvements

## Goal

Modernize how bashhub is packaged and distributed to eliminate the hard dependency on a pre-installed system Python, reduce manual release toil, and adopt current Python packaging standards.

## Status

In progress — Phase 1 started.

## Findings

### Current approach
`install-bashhub.sh` does the following:
1. Finds a compatible Python (3.9–3.14) already on the system
2. Downloads `virtualenv.pyz` from GitHub to bootstrap an isolated venv at `~/.bashhub/env/`
3. Downloads the bashhub-client tarball directly from GitHub (hardcoded tag: `3.0.1`)
4. Runs `pip install .` inside that venv
5. Symlinks `bh` and `bashhub` into `~/.bashhub/bin/`

### Problems identified
- **Hard system Python dependency** — the root cause of the Python 3.14/npyscreen issue going undetected until after release
- **Not on PyPI** — install pulls a tarball from GitHub with a manually-bumped hardcoded version tag
- **Legacy `setup.py`** — `pyproject.toml` is the standard since PEP 517/518; packaging should be modernized without changing the current `install-bashhub.sh` installer path in Phase 1
- **`mock` in `install_requires`** — test-only dependency incorrectly listed as a runtime dependency
- **Exact-pinned deps in `install_requires`** — causes conflicts when installed alongside other packages; pinning belongs in a lockfile, not `install_requires`

## Steps

### Phase 1 — Quick fixes (low effort, high value)

- [x] Remove `mock==3.0.5` from `install_requires`; keep only in `tests_require`/`extras_require`
- [x] Relax exact version pins to minimum bounds (e.g. `requests>=2.28`) in `install_requires`
- [x] Migrate `setup.py` to `pyproject.toml`
  - `install_bashhub.py` is legacy/unused; the active install path is `install-bashhub.sh`, so no installer Python changes are needed in Phase 1

### Phase 2 — PyPI publishing + modern install

- [ ] Publish package to PyPI
- [ ] Update `install-bashhub.sh` to install via `uv tool install bashhub` (primary) or `pipx install bashhub` (fallback)
  - `uv` bundles its own Python — eliminates system Python requirement entirely
  - Remove the manual `virtualenv.pyz` bootstrap and GitHub tarball download
- [ ] Update install docs / README to reflect new install method

### Phase 3 — Platform distribution (medium effort)

- [ ] Add a Homebrew formula for macOS (`brew install bashhub`)
  - Homebrew manages its own Python, sidestepping version issues

### Phase 4 — Standalone binary (longer term)

- [ ] Evaluate PyInstaller or Nuitka for bundling a self-contained binary
  - No Python required on target system at all
  - Tradeoff: larger artifact, more complex release pipeline
  - Reference: how `ruff`, `uv`, and `gh` are distributed
