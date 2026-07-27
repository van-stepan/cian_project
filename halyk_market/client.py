# -*- coding: utf-8 -*-
"""Client for the Halyk Market merchant API ("Работа с заказами по API").

Endpoints follow the official documentation at
https://halyk-market.gitbook.io/anyqtama/massovye-operacii-i-integracii/rabota-s-zakazami-po-api

Two hosts are involved. Listing, waybills, OTP and courier lookups live on the
gateway (``halykmarket.kz/gw``); order state changes and the JSON:API
relationship endpoints live on ``api.halykmarket.com``.
"""

import hashlib
import json
import logging
import os
import stat
import time

import requests

from .config import Config


logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30
# Renew slightly before the server-side expiry so a long request cannot straddle it.
TOKEN_EXPIRY_SKEW = 60

# The token endpoint rate-limits (HTTP 429), so a token issued by one CLI run is
# cached on disk and reused by the next one until it expires.
DEFAULT_CACHE_DIR = os.path.join(
    os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"),
    "halyk_market",
)


def default_token_cache_path(config):
    """Per-credential cache file. The client id is hashed to keep BINs off disk."""

    fingerprint = hashlib.sha256(
        ("%s|%s" % (config.client_id, config.token_url)).encode("utf-8")
    ).hexdigest()[:16]

    return os.path.join(DEFAULT_CACHE_DIR, "token-%s.json" % fingerprint)


class OrderStatus(object):
    """Order statuses used by the API."""

    APPROVED_BY_BANK = "APPROVED_BY_BANK"        # new order, confirmed by the bank
    ACCEPTED_BY_MERCHANT = "ACCEPTED_BY_MERCHANT"  # accepted by the shop
    WAITING_COURIER = "WAITING_COURIER"          # courier requested
    COMPLETED = "COMPLETED"                      # handed over to the customer
    CANCELLED = "CANCELLED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"


class CancellationReason(object):
    """Values accepted by the cancellationReason attribute."""

    BUYER_CANCELLATION_BY_MERCHANT = "BUYER_CANCELLATION_BY_MERCHANT"  # buyer refused
    BUYER_NOT_REACHABLE = "BUYER_NOT_REACHABLE"                        # could not reach buyer
    MERCHANT_OUT_OF_STOCK = "MERCHANT_OUT_OF_STOCK"                    # out of stock


# Cancellation is only permitted before the order is handed to delivery.
CANCELLABLE_STATUSES = (OrderStatus.APPROVED_BY_BANK, OrderStatus.ACCEPTED_BY_MERCHANT)


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

    def __init__(self, config=None, timeout=DEFAULT_TIMEOUT, session=None,
                 token_cache_path=None, use_token_cache=True):
        self.config = (config or Config.from_env()).validate()
        self.timeout = timeout
        self.session = session or requests.Session()

        self.use_token_cache = use_token_cache
        self.token_cache_path = token_cache_path or default_token_cache_path(self.config)

        self._access_token = None
        self._token_expires_at = 0.0

        if self.use_token_cache:
            self._load_cached_token()

    # ----------------------------------------------------------- token cache

    def _load_cached_token(self):
        try:
            with open(self.token_cache_path, "r", encoding="utf-8") as fid:
                cached = json.load(fid)
        except (IOError, OSError, ValueError):
            return False

        token = cached.get("access_token")
        expires_at = float(cached.get("expires_at") or 0)

        if token and time.time() < expires_at:
            self._access_token = token
            self._token_expires_at = expires_at
            logger.info("Reusing cached token from %s", self.token_cache_path)
            return True

        return False

    def _store_cached_token(self):
        try:
            os.makedirs(os.path.dirname(self.token_cache_path), exist_ok=True)
            # The file holds a bearer token - keep it owner-readable only.
            fd = os.open(self.token_cache_path,
                         os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                         stat.S_IRUSR | stat.S_IWUSR)
            with os.fdopen(fd, "w", encoding="utf-8") as fid:
                json.dump({"access_token": self._access_token,
                           "expires_at": self._token_expires_at}, fid)
        except (IOError, OSError) as exc:
            # A cache failure must never break an otherwise working call.
            logger.warning("Could not write token cache %s: %s", self.token_cache_path, exc)

    def clear_token_cache(self):
        self._access_token = None
        self._token_expires_at = 0.0
        try:
            os.remove(self.token_cache_path)
            return True
        except OSError:
            return False

    # ------------------------------------------------------------------ auth

    def authenticate(self, force=False):
        """Fetch an access token, reusing the cached one until it nears expiry.

        The token endpoint expects a JSON body. It answers 500 - not 401 - to a
        form-encoded one, so the encoding matters more than it looks. It also
        rate-limits, hence the on-disk cache shared across CLI invocations.
        """

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
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise HalykMarketAuthError("Token request failed: %s" % exc,
                                       url=self.config.token_url)

        body = _decode(response)

        if response.status_code == 429:
            raise HalykMarketAuthError(
                "Token endpoint rate-limited this client (HTTP 429). Tokens live ~2 hours and "
                "are cached at %s - wait before requesting another." % self.token_cache_path,
                status_code=429,
                payload=body,
                url=self.config.token_url,
            )

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

        if self.use_token_cache:
            self._store_cached_token()

        return self._access_token

    @property
    def access_token(self):
        return self.authenticate()

    # --------------------------------------------------------------- request

    def request(self, method, path, base=None, params=None, json_body=None,
                extra_headers=None, retry_on_401=True):
        """Perform an authenticated call.

        ``path`` is resolved against ``base`` (defaults to the gateway) unless it
        is already a full URL.
        """

        if path.startswith("http"):
            url = path
        else:
            url = (base or self.config.gw_base) + "/" + path.lstrip("/")

        headers = {
            "Authorization": "Bearer " + self.authenticate(),
            "Accept": "application/json",
        }
        if json_body is not None:
            headers["Content-Type"] = "application/json"
        if extra_headers:
            headers.update(extra_headers)

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
            return self.request(method, path, base=base, params=params, json_body=json_body,
                                extra_headers=extra_headers, retry_on_401=False)

        body = _decode(response)

        if response.status_code >= 400:
            raise HalykMarketError(
                "%s %s returned HTTP %d" % (method.upper(), url, response.status_code),
                status_code=response.status_code,
                payload=body,
                url=url,
            )

        return body

    def gw_get(self, path, params=None):
        return self.request("GET", path, base=self.config.gw_base, params=params)

    def api_get(self, path, params=None):
        return self.request("GET", path, base=self.config.api_base, params=params)

    # ----------------------------------------------------------- read orders

    ORDERS_LIST_PATH = "/merchant/public/order/v2"
    ORDER_DETAIL_PATH = "/merchant/public/order/v1"
    PRODUCT_BY_ORDER_PATH = "/merchant/public/merchant/product/details-by-order"
    ORDERS_PATH = "/api/merchant/v1/orders"
    ORDER_ENTRIES_PATH = "/api/merchant/v1/orderentries"
    POINT_OF_SERVICE_PATH = "/api/merchant/v1/pointofservices"

    def get_orders(self, status=None, page=1, size=20, order_number=None,
                   start_date=None, end_date=None):
        """List the shop's orders.

        All filters are optional. Dates are ``YYYY-MM-DD``; with no date range
        the API returns the last three months. ``size`` is capped at 100.
        """

        if size is not None and size > 100:
            raise ValueError("size may not exceed 100, got %r" % size)

        params = {}
        for key, value in (("page", page), ("size", size), ("orderNumber", order_number),
                           ("status", status), ("startDate", start_date), ("endDate", end_date)):
            if value is not None:
                params[key] = value

        return self.gw_get(self.ORDERS_LIST_PATH, params=params)

    def get_new_orders(self, **kwargs):
        """Orders awaiting the merchant's acceptance."""

        kwargs.setdefault("status", OrderStatus.APPROVED_BY_BANK)
        return self.get_orders(**kwargs)

    def get_order(self, order_number):
        """Order detail by order number.

        This is also where the waybill, the Yandex courier OTP and the courier
        service details come from - they are fields on the same payload.
        """

        return self.gw_get(self.ORDER_DETAIL_PATH, params={"orderNumber": order_number})

    def get_order_entries(self, order_id):
        """Line items of an order (the customer's basket)."""

        return self.api_get("%s/%s/relationships/entries" % (self.ORDERS_PATH, order_id))

    def get_entry_product(self, entry_id):
        """The shop's product behind a single order line."""

        return self.api_get("%s/%s/relationships/product" % (self.ORDER_ENTRIES_PATH, entry_id))

    def get_entry_point_of_service(self, entry_id):
        """Pickup point for a self-collection order line."""

        return self.api_get("%s/%s/relationships/deliveryPointOfService"
                            % (self.ORDER_ENTRIES_PATH, entry_id))

    def get_point_of_service_city(self, point_of_service_id):
        return self.api_get("%s/%s/relationships/city"
                            % (self.POINT_OF_SERVICE_PATH, point_of_service_id))

    def get_products_by_order(self, order_ids):
        """Product details for one or more orders, by internal order id."""

        if isinstance(order_ids, (int, str)):
            order_ids = [order_ids]

        return self.request("POST", self.PRODUCT_BY_ORDER_PATH, base=self.config.gw_base,
                            json_body={"orderIds": [int(i) for i in order_ids]})

    # --------------------------------------------------------- mutate orders

    def update_order(self, order_id, code, status, attributes=None, extra_headers=None):
        """POST an order state change.

        Every mutation shares this envelope; the wrappers below fill in the
        status and any status-specific attributes.
        """

        payload_attributes = {"code": code, "status": status}
        if attributes:
            payload_attributes.update(attributes)

        body = {
            "data": {
                "type": "orders",
                "id": str(order_id),
                "attributes": payload_attributes,
            }
        }

        return self.request("POST", self.ORDERS_PATH, base=self.config.api_base,
                            json_body=body, extra_headers=extra_headers)

    def accept_order(self, order_id, code, count_place=None, pos_code=None):
        """Accept a new order (APPROVED_BY_BANK -> ACCEPTED_BY_MERCHANT).

        ``count_place`` and ``pos_code`` apply to Halyk Market delivery, where
        the courier collects a known number of packages from a known point.
        """

        attributes = {}
        if count_place is not None:
            attributes["countPlace"] = count_place
        if pos_code is not None:
            attributes["posCode"] = pos_code

        return self.update_order(order_id, code, OrderStatus.ACCEPTED_BY_MERCHANT,
                                 attributes=attributes)

    def request_courier(self, order_id, code):
        """Call a Halyk Market courier (ACCEPTED_BY_MERCHANT -> WAITING_COURIER)."""

        return self.update_order(order_id, code, OrderStatus.WAITING_COURIER)

    def send_customer_otp(self, order_id, code):
        """Send the handover OTP to the customer.

        Same call as completion but with an empty X-Security-Code, which asks the
        platform to issue and deliver a code instead of verifying one.
        """

        return self.update_order(
            order_id, code, OrderStatus.COMPLETED,
            extra_headers={"X-Security-Code": "", "X-Send-Code": "true"},
        )

    def complete_order(self, order_id, code, security_code):
        """Complete an order by confirming the customer's OTP."""

        if not security_code:
            raise ValueError(
                "security_code is required to complete an order; use send_customer_otp() "
                "first to have the code delivered to the customer."
            )

        return self.update_order(
            order_id, code, OrderStatus.COMPLETED,
            extra_headers={"X-Security-Code": str(security_code), "X-Send-Code": "true"},
        )

    def cancel_order(self, order_id, code, reason):
        """Cancel an order that has not yet been handed to delivery."""

        valid = vars(CancellationReason)
        if reason not in {v for k, v in valid.items() if not k.startswith("_")}:
            raise ValueError(
                "Unknown cancellation reason %r. Expected one of: %s"
                % (reason, ", ".join(sorted(v for k, v in valid.items() if not k.startswith("_"))))
            )

        return self.update_order(order_id, code, OrderStatus.CANCELLED,
                                 attributes={"cancellationReason": reason})


def _decode(response):
    """Return parsed JSON when possible, otherwise the raw text."""

    if not response.content:
        return None

    try:
        return response.json()
    except (ValueError, json.JSONDecodeError):
        return response.text
