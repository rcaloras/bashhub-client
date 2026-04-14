from bashhub.validation import (
    validate_email,
    validate_username,
    validate_password,
    USERNAME_MAX,
    EMAIL_MAX,
    PASSWORD_MIN,
)


class TestValidateEmail:
    def test_valid_email(self):
        assert validate_email("user@example.com") is None

    def test_valid_email_with_plus_and_dots(self):
        assert validate_email("first.last+tag@sub.example.co.uk") is None

    def test_empty(self):
        assert validate_email("") is not None

    def test_missing_at_sign(self):
        assert validate_email("userexample.com") is not None

    def test_missing_domain_dot(self):
        # Server rejects user@localhost; we mirror that.
        assert validate_email("user@localhost") is not None

    def test_whitespace(self):
        assert validate_email("user @example.com") is not None

    def test_too_long(self):
        long_email = ("a" * (EMAIL_MAX - 10)) + "@example.com"
        assert validate_email(long_email) is not None


class TestValidateUsername:
    def test_valid_simple(self):
        assert validate_username("alice") is None

    def test_valid_with_underscore_and_hyphen(self):
        assert validate_username("alice_bob-123") is None

    def test_valid_single_char(self):
        # Server allows 1 char minimum.
        assert validate_username("a") is None

    def test_valid_at_max_length(self):
        assert validate_username("a" * USERNAME_MAX) is None

    def test_empty(self):
        assert validate_username("") is not None

    def test_too_long(self):
        assert validate_username("a" * (USERNAME_MAX + 1)) is not None

    def test_rejects_space(self):
        assert validate_username("alice bob") is not None

    def test_rejects_special_chars(self):
        assert validate_username("alice!") is not None
        assert validate_username("alice@home") is not None
        assert validate_username("alice.bob") is not None


class TestValidatePassword:
    def test_valid(self):
        assert validate_password("a" * PASSWORD_MIN) is None

    def test_valid_long(self):
        assert validate_password("correcthorsebatterystaple") is None

    def test_empty(self):
        assert validate_password("") is not None

    def test_too_short(self):
        assert validate_password("a" * (PASSWORD_MIN - 1)) is not None
