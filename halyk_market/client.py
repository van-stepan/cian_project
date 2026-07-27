# -*- coding: utf-8 -*-
"""Thin client for the Halyk Market merchant API.

Covers the OAuth2 client_credentials handshake and the order endpoints used for
"работа с заказами по API". Every call goes through :meth:`HalykMarketClient.request`,
so endpoints that are not wrapped explicitly can still be reached without
touching this module.
"""

import json
import logging
import time

import requests

from .config import Config


logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30
# Renew slightly before the server-side expiry so a long request cannot straddle it.
TOKEN_EXPIRY_SKEW = 60


class HalykMarketError(Exception):
    """Raised when the API answers with a non-success status."""

    def __init__(self, message, status_code=None, payload=None, url=None):
        super(HalykMarketError, self).__init__(message)
        self.status_code = status_code
        self.payload = payload
        self.url = url


class HalykMarketAuthError(HalykMarketError):
    """Raised when the token endpoint refuses the client credentials."""


class HalykMarketClient(object):

    def __init__(self, config=None, timeout=DEFAULT_TIMEOUT, session=None):
        self.config = (config or Config.from_env()).validate()
        self.timeout = timeout
        self.session = session or requests.Session()

        self._access_token = None
        self._token_expires_at = 0.0

    # ------------------------------------------------------------------ auth

    def authenticate(self, force=False):
        """Fetch an access token, reusing the cached one until it nears expiry."""

        if not force and self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }

        logger.info("Requesting access token for %s at %s",
                    self.config.client_id, self.config.token_url)

        try:
            response = self.session.post(
                self.config.token_url,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise HalykMarketAuthError("Token request failed: %s" % exc,
                                       url=self.config.token_url)

        body = _decode(response)

        if response.status_code >= 400:
            raise HalykMarketAuthError(
                "Token endpoint returned HTTP %d" % response.status_code,
                status_code=response.status_code,
                payload=body,
                url=self.config.token_url,
            )

        if not isinstance(body, dict) or not body.get("access_token"):
            raise HalykMarketAuthError(
                "Token endpoint returned no access_token",
                status_code=response.status_code,
                payload=body,
                url=self.config.token_url,
            )

        self._access_token = body["access_token"]
        expires_in = int(body.get("expires_in") or 0)
        self._token_expires_at = time.time() + max(expires_in - TOKEN_EXPIRY_SKEW, 0)

        logger.info("Access token acquired, expires_in=%s", expires_in or "unknown")

        return self._access_token

    @property
    def access_token(self):
        return self.authenticate()

    # --------------------------------------------------------------- request

    def request(self, method, path, params=None, json_body=None, retry_on_401=True):
        """Perform an authenticated call against the API gateway.

        ``path`` may be a bare path ("/api/merchant/v1/orders") or a full URL.
        """

        url = path if path.startswith("http") else self.config.api_base + "/" + path.lstrip("/")

        headers = {
            "Authorization": "Bearer " + self.authenticate(),
            "Accept": "application/json",
        }
        if json_body is not None:
            headers["Content-Type"] = "application/json"

        logger.info("%s %s params=%s", method.upper(), url, params)

        try:
            response = self.session.request(
                method.upper(), url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise HalykMarketError("Request failed: %s" % exc, url=url)

        # A token can be revoked server-side before its stated expiry; retry once.
        if response.status_code == 401 and retry_on_401:
            logger.info("Got 401, refreshing token and retrying once")
            self.authenticate(force=True)
            return self.request(method, path, params=params, json_body=json_body,
                                retry_on_401=False)

        body = _decode(response)

        if response.status_code >= 400:
            raise HalykMarketError(
                "%s %s returned HTTP %d" % (method.upper(), url, response.status_code),
                status_code=response.status_code,
                payload=body,
                url=url,
            )

        return body

    def get(self, path, params=None):
        return self.request("GET", path, params=params)

    def post(self, path, json_body=None, params=None):
        return self.request("POST", path, params=params, json_body=json_body)

    # ---------------------------------------------------------------- orders

    ORDERS_PATH = "/api/merchant/v1/orders"

    def get_orders(self, filters=None, page=None, per_page=None, extra_params=None):
        """List orders.

        ``filters`` is a plain dict of order attributes and is encoded in the
        ``filter[orders][<field>]`` form the gateway expects::

            client.get_orders(filters={"code": "1234567"})
        """

        params = {}

        for field, value in (filters or {}).items():
            if value is None:
                continue
            params["filter[orders][%s]" % field] = value

        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if extra_params:
            params.update(extra_params)

        return self.get(self.ORDERS_PATH, params=params)

    def get_order_by_code(self, code):
        """Fetch a single order by its human-readable order code."""

        return self.get_orders(filters={"code": code})

    def get_order(self, order_id):
        """Fetch a single order by its numeric/UUID identifier."""

        return self.get("%s/%s" % (self.ORDERS_PATH, order_id))


def _decode(response):
    """Return parsed JSON when possible, otherwise the raw text."""

    if not response.content:
        return None

    try:
        return response.json()
    except (ValueError, json.JSONDecodeError):
        return response.text
