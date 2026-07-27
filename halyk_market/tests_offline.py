# -*- coding: utf-8 -*-
"""Exercise the client against a local stub of both Halyk hosts."""

import json
import os
import threading
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from halyk_market import HalykMarketClient, HalykMarketAuthError, OrderStatus
from halyk_market.config import Config

STATE = {"tokens_issued": 0, "gets": [], "posts": [], "expire_next": False}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode() if n else ""
        return raw

    def do_POST(self):
        p = urlparse(self.path).path
        raw = self._read()
        if p == "/gw/auth/token":
            assert self.headers["Content-Type"] == "application/json", self.headers["Content-Type"]
            form = json.loads(raw)
            if form == {"grant_type": "client_credentials",
                        "client_id": "HMM_000117600035", "client_secret": "sekret"}:
                STATE["tokens_issued"] += 1
                return self._send(200, {"access_token": "tok-%d" % STATE["tokens_issued"],
                                        "token_type": "Bearer", "expires_in": 7199})
            return self._send(401, {"error": "invalid_client"})
        if p == "/api/merchant/v1/orders":
            STATE["posts"].append((json.loads(raw), dict(self.headers)))
            return self._send(200, {"data": json.loads(raw)["data"]})
        self._send(404, {"error": "not found"})

    def do_GET(self):
        u = urlparse(self.path)
        STATE["gets"].append((u.path, parse_qs(u.query), self.headers.get("Authorization")))
        if STATE["expire_next"]:
            STATE["expire_next"] = False
            return self._send(401, {"error": "expired"})
        if u.path == "/gw/merchant/public/order/v2":
            return self._send(200, {"content": [], "numberOfElements": 0})
        return self._send(200, {"data": []})


server = HTTPServer(("127.0.0.1", 8731), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()

base = "http://127.0.0.1:8731"
cfg = Config(client_id="HMM_000117600035", client_secret="sekret",
             gw_base=base + "/gw", api_base=base)


def fresh():
    return HalykMarketClient(config=cfg, use_token_cache=False)


client = fresh()

# 1. token handshake sends a JSON body
assert client.authenticate() == "tok-1"
print("OK  token handshake (JSON body) -> tok-1")

# 2. in-memory caching: 3 calls, 1 issue
client.authenticate(); client.authenticate()
assert STATE["tokens_issued"] == 1
print("OK  in-memory token cache")

# 3. orders list -> gw host, correct params (no None values)
client.get_orders(status="APPROVED_BY_BANK", size=20, page=2)
path, params, auth = STATE["gets"][-1]
assert path == "/gw/merchant/public/order/v2"
assert params == {"status": ["APPROVED_BY_BANK"], "size": ["20"], "page": ["2"]}, params
assert auth == "Bearer tok-1"
print("OK  orders -> gw", params)

# 4. size cap
try:
    client.get_orders(size=101); raise SystemExit("FAIL size cap")
except ValueError as e:
    print("OK  size cap ->", e)

# 5. entries -> api host
client.get_order_entries("777")
path, _, _ = STATE["gets"][-1]
assert path == "/api/merchant/v1/orders/777/relationships/entries", path
print("OK  entries -> api host")

# 6. order detail -> gw v1 with orderNumber
client.get_order("0008449018-1")
path, params, _ = STATE["gets"][-1]
assert path == "/gw/merchant/public/order/v1" and params == {"orderNumber": ["0008449018-1"]}, (path, params)
print("OK  order detail -> gw v1", params)

# 7. accept order envelope
client.accept_order("11111111", "1111111111-1", count_place=1, pos_code="pp48")
body, headers = STATE["posts"][-1]
assert body == {"data": {"type": "orders", "id": "11111111", "attributes": {
    "code": "1111111111-1", "status": "ACCEPTED_BY_MERCHANT",
    "countPlace": 1, "posCode": "pp48"}}}, body
print("OK  accept_order envelope")

# 8. complete requires OTP + sends security headers
try:
    client.complete_order("1", "c", ""); raise SystemExit("FAIL otp required")
except ValueError as e:
    print("OK  complete requires OTP ->", str(e)[:40], "...")
client.complete_order("11111111", "1111111111-1", "4007")
body, headers = STATE["posts"][-1]
assert body["data"]["attributes"]["status"] == "COMPLETED"
assert headers.get("X-Security-Code") == "4007" and headers.get("X-Send-Code") == "true"
print("OK  complete_order sends X-Security-Code/X-Send-Code")

# 9. send-otp sends empty security code
client.send_customer_otp("11111111", "1111111111-1")
_, headers = STATE["posts"][-1]
assert headers.get("X-Security-Code") == "" and headers.get("X-Send-Code") == "true"
print("OK  send_customer_otp -> empty X-Security-Code")

# 10. cancel validates reason
try:
    client.cancel_order("1", "c", "NOPE"); raise SystemExit("FAIL bad reason")
except ValueError as e:
    print("OK  cancel rejects bad reason")
client.cancel_order("11111111", "1111111111-1", "MERCHANT_OUT_OF_STOCK")
body, _ = STATE["posts"][-1]
assert body["data"]["attributes"] == {"code": "1111111111-1", "status": "CANCELLED",
                                       "cancellationReason": "MERCHANT_OUT_OF_STOCK"}
print("OK  cancel_order envelope")

# 11. 401 mid-session -> one refresh + retry
STATE["expire_next"] = True
client.get_orders()
assert STATE["tokens_issued"] == 2
_, _, auth = STATE["gets"][-1]
assert auth == "Bearer tok-2"
print("OK  401 -> refresh + retry with", auth)

# 12. bad secret surfaces auth error
bad = HalykMarketClient(config=Config(client_id="HMM_000117600035", client_secret="wrong",
                        gw_base=base + "/gw", api_base=base), use_token_cache=False)
try:
    bad.authenticate(); raise SystemExit("FAIL bad secret")
except HalykMarketAuthError as e:
    assert e.status_code == 401
    print("OK  bad secret -> 401")

# 13. missing creds rejected before network
try:
    HalykMarketClient(config=Config(), use_token_cache=False); raise SystemExit("FAIL")
except ValueError:
    print("OK  missing creds rejected")

# 14. build_client_id
from halyk_market.config import build_client_id
assert build_client_id("000117600035") == "HMM_000117600035"
assert build_client_id("HMM_000117600035") == "HMM_000117600035"
print("OK  build_client_id")

# 15. disk token cache shared across client instances
import tempfile
cache = os.path.join(tempfile.mkdtemp(), "tok.json")
STATE["tokens_issued"] = 0
c1 = HalykMarketClient(config=cfg, token_cache_path=cache)
c1.authenticate()
c2 = HalykMarketClient(config=cfg, token_cache_path=cache)  # new process would look like this
c2.authenticate()
assert STATE["tokens_issued"] == 1, STATE["tokens_issued"]
assert oct(os.stat(cache).st_mode)[-3:] == "600", oct(os.stat(cache).st_mode)
print("OK  disk token cache reused across instances, perms 600")

print("\nALL CHECKS PASSED")
server.shutdown()
