# Stabilize the `mac` system fingerprint in bashhub-client

## Context

Users occasionally hit a bug where a machine that's already registered
with the server is not recognized as such, forcing them to re-register
it under a new name (the server enforces per-user unique system names).
Their command history ends up split across two "systems" in the server
— effectively duplicate records for the same box.

The "mac" was originally meant to be a stable, globally-unique client-
side fingerprint for a machine. In practice the current implementation
drifts, and any time it does, setup (and, more importantly, `bashhub
update`) fails to recognize the box.

## Root cause

[`bashhub/bashhub_setup.py:120`](bashhub/bashhub_setup.py:120) —
`get_mac_address()`:

```python
def get_mac_address() -> str:
    mac_int = uuid.getnode()
    if (mac_int >> 40) & 1:          # getnode failed, random multicast value
        hostname = socket.gethostname()
        return hostname
    return str(mac_int)
```

`uuid.getnode()` is not a stable machine fingerprint:

1. **Multi-interface drift.** `getnode()` walks the system's NICs and
   returns the first MAC it finds. On any box with more than one
   interface (wifi + ethernet + docker0 + VPN/tun + vboxnet…) which
   interface "wins" is not guaranteed to be stable across runs.
   Bringing up/down a VPN, starting Docker, plugging in ethernet, or
   rebooting into a different NIC order can change the answer.
2. **Randomized-MAC fallback.** If `getnode()` can't find any hardware
   MAC it synthesizes a random multicast value (detected by the
   `(mac_int >> 40) & 1` check). We fall through to
   `socket.gethostname()` then — but since we don't persist, the next
   run may succeed where this one failed, silently flipping between
   numeric-mac and hostname form.
3. **Never persisted.** The mac is recomputed from scratch on every
   invocation. `~/.bashhub/config` stores `access_token`, `system_name`,
   `url`, `save_commands`, `debug`, `filter` — but not the mac
   ([`bashhub_globals.py:23`](bashhub/bashhub_globals.py:23)). The
   client has no source of truth for "what mac did we agree on with
   the server."

### Where drift actually bites users: the `bashhub update` path

This is the part worth spelling out, because it's what turns an
occasional edge case into a recurring one.

`bashhub update` downloads and executes `https://bashhub.com/setup`.
That installer script:

1. Backs up `~/.bashhub/config`, deletes `~/.bashhub`, reinstalls the
   client, restores the config.
2. Runs `bashhub util update-system-info`, which calls
   [`bashhub_setup.update_system_info()`](bashhub/bashhub_setup.py:134)
   → `get_mac_address()` → `patch_system(patch, mac)` →
   `PATCH /api/v1/system/<mac>`.
3. **If that exits non-zero, the installer falls through to running
   `bashhub setup` from scratch.**

Look at `patch_system()` in
[`rest_client.py:190`](bashhub/rest_client.py:190): any exception,
including a 404 when the mac has drifted, returns `None`.
[`bashhub.py:210`](bashhub/bashhub.py:210) then exits 1. The installer
catches that and drops into `bashhub setup`, which:

- Calls `handle_system_information()`
  ([`bashhub_setup.py:147`](bashhub/bashhub_setup.py:147)).
- `get_system_information(mac)` 404s (same drifted mac).
- Prompts the user for a system name, defaulting to the hostname.
- Calls `register_system(...)` with that name.
- Server 409s because the user already has a system with that name
  ([`bashhub-server/api/views/system.py:43`](../bashhub-server/api/views/system.py:43)).
- User is forced to type a different name → split history.

So the most common trigger for this bug is not a deliberate setup
re-run — it's a routine `bashhub update`. Any fix must heal both the
PATCH path (`update_system_info`) and the register path
(`handle_system_information`).

### Server-side capabilities we can lean on (no server change needed)

- `GET /api/v1/system` already falls back to `name=` when `mac=` misses
  ([`system.py:75`](../bashhub-server/api/views/system.py:75)).
- `PATCH /api/v1/system/<old_mac>` already allows updating the `mac`
  field in the body
  ([`system.py:126`](../bashhub-server/api/views/system.py:126)).
- `unique_together = [("user", "mac")]` is enforced in the DB; name is
  only a view-layer check.

Those three together mean a client-only fix can both recognize an
existing box by name and rewrite its mac to a new stable value.

## Recommended approach (client-only, Option B)

Treat `~/.bashhub/config` as the source of truth for the mac, and make
both the PATCH and register paths self-heal via the server's name
fallback. No server changes.

### Config-first mac resolution

Add a `mac` key to `~/.bashhub/config` and a `BH_MAC` accessor in
[`bashhub_globals.py`](bashhub/bashhub_globals.py:61).

`get_mac_address()` becomes:

1. If `BH_MAC` is set in config, return it. Done.
2. Otherwise, compute via `uuid.getnode()` (today's logic, unchanged).
   Do not persist here — persisting happens only after we confirm the
   value with the server (on successful register / PATCH / name-
   fallback resolve). That way a transient bad value never gets pinned
   into config.

### `update_system_info()` self-heal (the hot path)

Current flow:

```
mac = get_mac_address()
PATCH /api/v1/system/<mac>  {hostname, clientVersion}
```

New flow:

```
mac = get_mac_address()                     # config first, then uuid.getnode()
try PATCH /api/v1/system/<mac>  {hostname, clientVersion}
  on success:
    if config had no mac yet, write mac to config  # eager migration
  on 404 AND BH_SYSTEM_NAME is set:
    GET /api/v1/system?name=<BH_SYSTEM_NAME>          # server returns {mac: server_mac, ...}
    if found:
      PATCH /api/v1/system/<server_mac>  {mac: mac, hostname, clientVersion}
      write mac to config
    else:
      return failure (falls through to `bashhub setup` as today)
```

Eager migration is automatic here: every user who runs `bashhub
update` immediately gets their current mac pinned into config on the
next successful PATCH, closing the drift window. Users who are
*already* broken self-heal on the same call.

### `handle_system_information()` self-heal (setup path)

Current flow does `get_system_information(mac)` and, on None, prompts
to register a new system.

New flow:

1. `mac = get_mac_address()` (config first).
2. `get_system_information(mac=mac, name=BH_SYSTEM_NAME)` — passes
   **both** params on the same request so the server's existing
   `mac → name` fallback resolves in one round-trip. No extra client
   logic needed for the "config present but drifted" case.
3. If found and `system.mac != mac`: PATCH to reconcile the server's
   mac to `mac` (same mechanism as above). Write `mac` to config.
4. If found and mac already matches: write `mac` to config (migrates
   healthy existing users who ran `bashhub setup` without ever running
   `bashhub update`).
5. If not found: register as today, then write `mac` to config on
   success.

Because `BH_SYSTEM_NAME` is loaded lazily from config at import time,
the name fallback only kicks in for users who already have a config
— i.e., exactly the "already registered, config intact" case. The
common path to this bug (`bashhub update` installer preserves config
across updates, so `BH_SYSTEM_NAME` always survives) is fully
covered.

**Out of scope for this PR: config-loss recovery.** If `~/.bashhub/
config` is wiped entirely, `BH_SYSTEM_NAME` is empty, the name
fallback is a no-op, and we fall through to register — same as
today's behavior. A pre-register `GET ?name=<typed_name>` reclaim
would cover this, but it's unsafe because the same system name
(typically the hostname like "MacBook-Pro" or "localhost") is very
commonly used across multiple distinct machines, and auto-reclaiming
by name would silently merge two real systems into one. Tracked as a
follow-up.

### Why a stable OS-level machine ID is a follow-up, not part of this PR

Under the config-first design above, `uuid.getnode()` is only called
once per machine as long as the config file is intact — on the very
first `bashhub setup` run, before anything has been written to
config. Within that single process, whatever value `getnode()` returns
is self-consistent: the exact same value gets sent to the server *and*
written to local config in the same invocation. So drift across runs
is structurally impossible while config lives.

The remaining exposure is **config loss / corruption**. This PR
deliberately doesn't try to fix that case (see the out-of-scope note
in the setup-path flow — name-based auto-reclaim is unsafe because of
hostname collisions across machines). A stable OS-level machine ID
would eliminate the exposure entirely without any name matching: a
rebuilt config would recompute the same mac that's on the server, and
the normal mac-lookup path would succeed without user interaction or
unsafe name collisions.

That's the right long-term fix but is independent of everything else
in this plan, so it's tracked as a follow-up. See the "Follow-up"
section.

### Option A (persist-only, no self-heal) is rejected

Option A alone does nothing for users who are already broken — their
next `bashhub update` still 404s the PATCH, falls through to `bashhub
setup`, and creates a duplicate. The whole point of the fix is to
recover those users, so self-heal is table stakes.

### Option D (server-side fix) is rejected

Relaxing the server's "duplicate name" check to reclaim same-user/
same-name systems would centralize the fix, but it changes API
semantics in a way other clients could depend on, and it still leaves
`update_system_info()` silently 404ing and falling through to setup.
It's the wrong lever.

## Critical files

- [`bashhub/bashhub_setup.py`](bashhub/bashhub_setup.py) —
  `get_mac_address()` (L120), `update_system_info()` (L134),
  `handle_system_information()` (L141). Main edits live here.
- [`bashhub/bashhub_globals.py`](bashhub/bashhub_globals.py) —
  `write_to_config_file` / `get_from_config` (L23, L44). Add a
  `BH_MAC` accessor alongside `BH_SYSTEM_NAME` (L61).
- [`bashhub/rest_client.py`](bashhub/rest_client.py) —
  `get_system_information()` (L141) needs an optional `name` param
  that the server already supports. `patch_system()` (L190) stays as
  is — the self-heal path calls it a second time with a different
  URL mac.
- [`bashhub/model/system.py`](bashhub/model/system.py) — no changes;
  `SystemPatch` already carries `mac`.
- [`tests/test_bashhub_setup.py`](tests/test_bashhub_setup.py) — add
  coverage for config-first resolution, PATCH-path self-heal, and
  register-path self-heal.

## Follow-ups (separate PRs)

### 1. Adopt a stable OS-level machine ID (primary follow-up)

Goal: eliminate `uuid.getnode()` as the seed value for `mac`, so that
even a completely wiped `~/.bashhub/config` recomputes an ID that
matches what's already on the server. Turns config loss from "falls
through to register a duplicate system" into a silent no-op.

**Library:** [`py-machineid`](https://pypi.org/project/py-machineid/)
(PyPI package `py-machineid`, MIT-licensed, small, maintained). It
wraps the OS-native stable identifiers:

- Linux: `/etc/machine-id` (fallback `/var/lib/dbus/machine-id`)
- macOS: `IOPlatformUUID` via `ioreg -rd1 -c IOPlatformExpertDevice`
- Windows: `MachineGuid` from `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography`
- FreeBSD: `/etc/hostid`

It exposes `machineid.hashed_id('bashhub')` which HMAC-SHAs the raw
identifier with a caller-supplied salt, so we send a derived hash
over the wire rather than leaking a raw OS ID.

**Migration strategy (backwards compatible):**

1. `get_mac_address()` still reads from config first — existing
   installs keep the mac value they already negotiated with the
   server forever.
2. On a *fresh* run with no config entry, compute via `py-machineid`
   first. Only fall back to `uuid.getnode()` → hostname if the
   library raises (e.g. `/etc/machine-id` missing in a locked-down
   container).
3. Existing users only see a change if they wipe their config — at
   which point the recomputed mac matches the server and nothing
   else has to happen.

**Open question for the follow-up:** do we want a one-time
`py-machineid` capture for users who already have a config, and
opportunistically PATCH the server to the hashed value? That would
converge everyone onto the stable ID over time. Probably yes, but
that's a design question for the follow-up PR.

### 2. Name-based system reclaim (lower priority)

If config-loss recovery turns out to be a recurring user complaint
*after* the stable-ID follow-up ships, revisit pre-register name
lookup in `handle_system_information()`. The safety concern is that
the same system name (typically the hostname) is commonly used across
multiple distinct machines, so an automatic reclaim-by-name risks
silently merging two real systems. If we pursue this, any reclaim
path should require explicit user confirmation ("A system named
'MacBook-Pro' already exists — is this the same machine?") rather
than being automatic.

## Verification

- Unit tests (extend `tests/test_bashhub_setup.py`):
  - `get_mac_address()` returns the config value when set, ignoring
    `uuid.getnode()`.
  - `get_mac_address()` falls back to `uuid.getnode()` when config is
    empty.
  - `update_system_info()` happy path: PATCH succeeds, mac written to
    config when it wasn't already there.
  - `update_system_info()` self-heal: first PATCH 404s with a stored
    `BH_SYSTEM_NAME`, follows up with a GET-by-name, second PATCH
    targets the server's mac with the client mac in the body, config
    is backfilled.
  - `update_system_info()` no-recovery: 404 with no
    `BH_SYSTEM_NAME` → returns failure unchanged.
  - `handle_system_information()` happy path: finds via mac, writes
    config.
  - `handle_system_information()` self-heal (config present but
    drifted): passes `name=` on the initial GET, finds by name,
    reconciles mac via PATCH, writes config.
  - `handle_system_information()` brand-new: GET 404 with no stored
    name, registers and writes config.
  - `handle_system_information()` config-wiped: GET 404 with no
    stored name, registers a new system (unchanged from today — this
    case is deliberately out of scope and tracked as a follow-up).
- Lint / type:
  - `pytest`, `mypy bashhub/`, `ruff check bashhub/` all green.
- End-to-end against a local bashhub-server:
  - Fresh install: `bashhub setup`, confirm `mac` in
    `~/.bashhub/config`, confirm server has matching value.
  - Simulate drift via `update`: edit the config's `mac` to a
    different value, run `bashhub util update-system-info`, confirm
    the client self-heals via name lookup and the server's mac is
    rewritten to the edited value. Confirm no fallback-to-setup.
  - Simulate drift via `setup`: delete `mac` from config, run
    `bashhub setup`, confirm it reconciles via name without
    prompting for a new system name or creating a duplicate.
  - Confirm idempotence: running update/setup a second time is a
    no-op.
