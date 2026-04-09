# Client-Side Validation & Registration Flow Improvements

## Goal

Add client-side input validation to the registration and login setup flow, and improve the overall UX so users get clear, immediate feedback before any API call is made. Currently **zero validation** exists on the client — all input is sent directly to the API, and errors surface as raw API response text.

## Status

Not started.

## Findings

### Current flow (step by step)
1. Ask if new user → Y/N
2. If new: collect email, username, password → confirm → POST `/api/v1/user`
3. Login: collect username, password → POST `/api/v1/login` (up to 4 retries)
4. System: derive MAC/hostname → optionally prompt system name → POST `/api/v1/system`
5. Write tokens to `~/.bashhub/config`

### Validation gaps
- **Email**: no format check, can be empty
- **Username**: no length or character check, can be empty
- **Password**: no minimum length, no complexity, can be empty, no confirmation prompt
- **System name**: can be empty (silently falls back to hostname — this is fine, but not communicated)
- All API error messages are printed as raw `response.text` — format is inconsistent and not user-friendly

### Key files
- `bashhub/bashhub_setup.py` — `get_new_user_information()`, `get_user_information_and_login()`, `handle_system_information()`
- `bashhub/rest_client.py` — `register_user()`, `login_user()`, `register_system()`
- `bashhub/model/command.py` — `RegisterUser`, `LoginForm`, `LoginResponse`
- `tests/test_bashhub_setup.py` — existing tests (covers MAC/system, not registration)

---

## Steps

### Phase 1 — Input validation

- [ ] **Email**: validate format before sending to API
  - Must contain `@` and a domain (e.g. simple regex or stdlib check)
  - Must not be empty
  - Show inline error and re-prompt on failure

- [ ] **Username**: validate before sending to API
  - Must not be empty
  - Minimum 3 characters, maximum 30
  - Alphanumeric + underscores/hyphens only (no spaces or special characters)
  - Show inline error and re-prompt on failure

- [ ] **Password**: validate before sending to API
  - Must not be empty
  - Minimum 8 characters
  - Add a confirm password prompt (re-enter to verify match)
  - Show inline error and re-prompt on failure

- [ ] **System name**: communicate the hostname default explicitly
  - Currently silently defaults to hostname if blank — make this visible to the user

### Phase 2 — Error message improvements

- [ ] Parse and clean up API error responses in `rest_client.py`
  - Currently prints raw `response.text` for 409/422/401 — this can contain JSON or HTML
  - Extract a clean message string, fall back to a generic one if parsing fails

- [ ] Improve registration failure messaging
  - Currently: `"registering a new user failed"` with no detail
  - Should distinguish: username taken vs. email taken vs. server error

- [ ] Improve login failure messaging
  - Currently: raw API text for 401
  - Should be: `"Incorrect username or password."` consistently
  - Keep the password reset URL hint on final failure

- [ ] Improve system registration failure messaging
  - Currently: `"Looks like registering your system failed. Lets retry."` (also a typo: "Lets" → "Let's")

### Phase 3 — Tests

- [ ] Unit tests for each validation function (email, username, password)
- [ ] Test that invalid inputs re-prompt rather than calling the API
- [ ] Test clean error message extraction from API responses
- [ ] Test registration flow with mocked API returning 409 (conflict) and 422 (validation error)
- [ ] Test login flow with mocked 401 response
