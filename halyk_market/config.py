# -*- coding: utf-8 -*-
"""Credential and endpoint configuration for the Halyk Market merchant API.

Secrets are never hardcoded here. They are read from the process environment,
optionally seeded from a local ``.env`` file that is excluded from git.

The API is split across two hosts:

``gw_base``   https://halykmarket.kz/gw   - token issuance, order listing,
                                            waybill / OTP / courier lookups
``api_base``  https://api.halykmarket.com - order mutations and the
                                            JSON:API relationship endpoints
"""

import os


PROD = "prod"
TEST = "test"

ENVIRONMENTS = {
    PROD: {
        "gw_base": "https://halykmarket.kz/gw",
        "api_base": "https://api.halykmarket.com",
    },
    TEST: {
        "gw_base": "https://test2.halykmarket.com/gw",
        # The documentation only ever names the test gateway; the test host for
        # the api.* surface is unconfirmed. Override via HALYK_API_BASE if needed.
        "api_base": "https://test2.halykmarket.com",
    },
}

CLIENT_ID_PREFIX = "HMM_"


def load_dotenv(path=None):
    """Seed os.environ from a KEY=VALUE file. Existing variables win."""

    if path is None:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

    if not os.path.isfile(path):
        return False

    with open(path, "r", encoding="utf-8") as fid:
        for line in fid:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            # Only strip quotes when they wrap the whole value - the secret may
            # legitimately contain brackets, slashes and other punctuation.
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            os.environ.setdefault(key, value)

    return True


def build_client_id(bin_number):
    """client_id is the shop BIN/IIN prefixed with HMM_ (e.g. HMM_000117600035)."""

    bin_number = str(bin_number).strip()
    if bin_number.startswith(CLIENT_ID_PREFIX):
        return bin_number

    digits = "".join(ch for ch in bin_number if ch.isdigit())
    if len(digits) != 12:
        raise ValueError(
            "BIN/IIN must contain exactly 12 digits, got %d (%r)" % (len(digits), bin_number)
        )

    return CLIENT_ID_PREFIX + digits


class Config(object):

    def __init__(self, client_id=None, client_secret=None, environment=PROD,
                 gw_base=None, api_base=None):

        if environment not in ENVIRONMENTS:
            raise ValueError("Unknown environment %r, expected one of %s"
                             % (environment, sorted(ENVIRONMENTS)))

        self.environment = environment
        self.client_id = client_id
        self.client_secret = client_secret
        self.gw_base = (gw_base or ENVIRONMENTS[environment]["gw_base"]).rstrip("/")
        self.api_base = (api_base or ENVIRONMENTS[environment]["api_base"]).rstrip("/")

    @property
    def token_url(self):
        return self.gw_base + "/auth/token"

    @classmethod
    def from_env(cls, environment=None, dotenv_path=None):
        """Build a config from HALYK_* environment variables.

        HALYK_CLIENT_ID    full client id, or
        HALYK_BIN          12-digit BIN/IIN, turned into HMM_<bin>
        HALYK_CLIENT_SECRET
        HALYK_ENV          prod | test
        HALYK_GW_BASE      optional override
        HALYK_API_BASE     optional override
        """

        load_dotenv(dotenv_path)

        client_id = os.environ.get("HALYK_CLIENT_ID")
        if not client_id:
            bin_number = os.environ.get("HALYK_BIN")
            if bin_number:
                client_id = build_client_id(bin_number)

        if environment is None:
            environment = os.environ.get("HALYK_ENV", PROD)

        return cls(
            client_id=client_id,
            client_secret=os.environ.get("HALYK_CLIENT_SECRET"),
            environment=environment,
            gw_base=os.environ.get("HALYK_GW_BASE"),
            api_base=os.environ.get("HALYK_API_BASE"),
        )

    def validate(self):
        missing = []
        if not self.client_id:
            missing.append("HALYK_CLIENT_ID (or HALYK_BIN)")
        if not self.client_secret:
            missing.append("HALYK_CLIENT_SECRET")

        if missing:
            raise ValueError(
                "Missing credentials: %s. Set them in the environment or in a local .env file "
                "(see .env.example)." % ", ".join(missing)
            )

        return self

    def masked(self):
        """Safe-to-log view of the config."""

        secret = self.client_secret or ""
        if len(secret) > 4:
            shown = secret[:2] + "*" * (len(secret) - 4) + secret[-2:]
        else:
            shown = "*" * len(secret)

        return {
            "environment": self.environment,
            "client_id": self.client_id,
            "client_secret": shown,
            "token_url": self.token_url,
            "gw_base": self.gw_base,
            "api_base": self.api_base,
        }
