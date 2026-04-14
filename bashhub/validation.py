"""Client-side validation for registration fields.

Rules mirror the bashhub-server constraints where practical. Each validator
returns None if the input is valid, or a user-facing error string otherwise.
The reserved-username list and uniqueness checks are intentionally not
mirrored here -- they are enforced server-side and surfaced via API errors.
"""
import re

# Matches server regex in bashhub-server api/views/user.py
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9\-_]+$")
USERNAME_MIN = 1
USERNAME_MAX = 39

EMAIL_MAX = 254
# Pragmatic format check: non-empty local, @, non-empty domain with a dot.
# Matches what the server actually verifies (has @ and a dot in the domain).
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Client-only guardrail. The server enforces no minimum, but we reject
# obviously-weak passwords here for UX.
PASSWORD_MIN = 8


def validate_email(email):
    if not email:
        return "Email cannot be empty."
    if len(email) > EMAIL_MAX:
        return "Email must be %d characters or fewer." % EMAIL_MAX
    if not EMAIL_REGEX.match(email):
        return "That doesn't look like a valid email address."
    return None


def validate_username(username):
    if not username:
        return "Username cannot be empty."
    if len(username) < USERNAME_MIN or len(username) > USERNAME_MAX:
        return "Username must be between %d and %d characters." % (
            USERNAME_MIN, USERNAME_MAX)
    if not USERNAME_REGEX.match(username):
        return ("Username may only contain letters, numbers, "
                "underscores, and hyphens.")
    return None


def validate_password(password):
    if not password:
        return "Password cannot be empty."
    if len(password) < PASSWORD_MIN:
        return "Password must be at least %d characters." % PASSWORD_MIN
    return None
