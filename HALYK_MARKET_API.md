# Halyk Market — merchant API (memory file)

Working notes for the Halyk Market (Anyqtama) merchant API integration. This is the
shared memory file for the project: everything we establish about the API lands here so
a later session does not have to rediscover it.

Primary documentation:
<https://halyk-market.gitbook.io/anyqtama/massovye-operacii-i-integracii/rabota-s-zakazami-po-api>

Each fact below is tagged:

- **[confirmed]** — read out of the official documentation or a Halyk-issued email.
- **[unverified]** — inferred from search snippets / secondary sources, not yet checked
  against a live call or the doc page itself.
- **[open]** — known gap.

---

## 1. Credentials

| Field | Value | Source |
|---|---|---|
| `client_id` | `HMM_000117600035` | built from BIN/IIN `000117600035` |
| `client_secret` | stored in local `.env`, never committed | reset email, 27.07.2026 |

**[confirmed]** `client_id` is the shop identifier in the form `HMM_<БИН>` — the doc's
example is `HMM_000000000000`, twelve digits. Our BIN/IIN is `000117600035`, so the
client id is `HMM_000117600035`.

**[confirmed]** `client_id` is sent by the account manager. `client_secret` is emailed
automatically when the API is switched on, and re-issued on password reset — the reset
mail comes from `api-noreply@halykmarket.com` with subject «Новый пароль».

**[open]** The secret currently in `.env` was transcribed from a phone screenshot, and it
contains characters that are easy to misread in a proportional font — an `O`/`0` pair and
two bracket characters. If the token call returns 401, re-check the value character by
character against the original email before assuming anything else is wrong. Rotate the
secret once the integration works: it has travelled through a screenshot and a chat.

Credentials live in `.env` (gitignored). `.env.example` documents the variables.

---

## 2. Authorization

**[confirmed]** OAuth2 `client_credentials`. Request attributes:

| Field | Description | Example |
|---|---|---|
| `grant_type` | always `client_credentials` | `client_credentials` |
| `client_id` | shop id, `HMM_<БИН>` | `HMM_000000000000` |
| `client_secret` | shop secret key | `xxxxxxxxxxxxxxxxxxxxxx` |

Token endpoints:

| Environment | URL | Confidence |
|---|---|---|
| prod | `https://halykmarket.kz/gw/auth/token` | [unverified] |
| test | `https://test2.halykmarket.com/gw/auth/token` | [unverified] |

**[unverified]** Response is the usual OAuth2 shape — `access_token`, `token_type:
"Bearer"`, `expires_in: 7199` (~2 h). The client caches the token and refreshes it 60 s
before expiry, and retries once on a 401.

**[open]** Whether the body is form-encoded or JSON is not confirmed. The client sends
`application/x-www-form-urlencoded`, which is the OAuth2 default; if the gateway rejects
it, switch `authenticate()` to `json=payload`.

---

## 3. Orders

**[unverified]** `GET https://api.halykmarket.com/api/merchant/v1/orders`, with
`Authorization: Bearer <access_token>`.

Filtering uses bracket syntax — `filter[orders][code]=1234567`. The client's
`get_orders(filters={"code": ...})` builds that encoding.

Note the host split: the token is issued by `halykmarket.kz`, while the API gateway is
`api.halykmarket.com`. `Config` keeps `token_url` and `api_base` separate for this
reason.

**[open]** Not yet captured — these need the doc pages, which are currently unreachable
(see §6):

- The exact order list response schema and pagination parameters.
- The full order status vocabulary and the allowed transitions.
- Order confirmation, transfer-to-delivery, and cancellation endpoints.
- Pickup-point retrieval (`2.3 Получение точки продаж заказа (для самовывоза)`).
- Yandex courier OTP retrieval (`3.1.4`).
- Error codes.

Until those are filled in, `client.request("POST", "/api/merchant/v1/...", json_body=...)`
and the `raw` CLI subcommand reach any endpoint without code changes.

**[confirmed]** The documentation splits order handling into two modes — обычный режим
(normal) and режим предзаказа (pre-order) — with separate endpoint trees. We have not yet
established which mode our shop is on; the endpoints differ, so confirm this before
writing order-mutation code.

**[confirmed]** After an order reaches «Выполнен», payout happens within 3 business days.

---

## 4. Usage

```bash
cp .env.example .env      # then fill in the secret

python -m halyk_market.cli config                      # masked config, no network
python -m halyk_market.cli token                       # verify credentials
python -m halyk_market.cli orders --per-page 20
python -m halyk_market.cli order 1234567
python -m halyk_market.cli raw GET /api/merchant/v1/orders --param 'page=2'
python -m halyk_market.cli --env test token             # test2 environment
```

Add `-v` to log every HTTP call.

From Python:

```python
from halyk_market import HalykMarketClient

client = HalykMarketClient()
orders = client.get_orders(filters={"code": "1234567"})
```

Requires `requests`.

---

## 5. Layout

```
halyk_market/
    config.py   credentials, environments, HMM_<БИН> construction, .env loading
    client.py   token handshake + caching, authenticated request layer, order calls
    cli.py      command line entry point
.env.example    documented variables
.env            real credentials, gitignored
```

The module is Python 3 and standalone — it shares nothing with the Python 2 CIAN code in
`main.py` / `support/`.

---

## 6. Environment note

`halykmarket.kz`, `api.halykmarket.com`, `test2.halykmarket.com` and
`halyk-market.gitbook.io` are all refused by the egress policy of the Claude Code web
sandbox (`403` on CONNECT). So from that sandbox:

- the documentation cannot be read directly — only via search snippets, hence the
  `[unverified]` tags above;
- no live call has been made, so nothing in §2–§3 has been exercised end to end.

Run the CLI from the laptop, or allow those hosts in the environment's network policy,
to verify.
