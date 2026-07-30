# Halyk Market (HM) — Order & Stock Sync Integration Handout

Self-contained spec for adding **Halyk Market** to the mp-warehouse integration layer
(alongside WB/Ozon). Covers **order intake** and **stock/price push**. Everything below is
API-verified against the live merchant account unless marked `[open]`.

Merchant: **Bricase KZ**, БИН/ИИН **000117600035**, `client_id = HMM_000117600035`
(`client_id = "HMM_" + BIN`). Catalogue = phone cases; 155 SKUs already live.

---

## 0. Credentials (env — never hardcode)
```
HALYK_CLIENT_ID=HMM_000117600035
HALYK_CLIENT_SECRET=<from Halyk reset email, no quotes>   # secret — keep in vault/.env, gitignored
HALYK_ENV=prod
```
No secret values in this doc. Same secret authorizes everything below.

---

## 1. Auth  — `POST https://halykmarket.kz/gw/auth/token`
- **Body is JSON** (form-encoded → HTTP 500, not 401):
  `{"grant_type":"client_credentials","client_id":"HMM_000117600035","client_secret":"…"}`
- Response: `access_token` (JWT), `token_type:"Bearer"`, `expires_in:7199` (~2h).
- Use `Authorization: Bearer <token>` on all calls.
- **Rate-limited (HTTP 429)** if you mint a token per call → **cache & reuse** until expiry.

## 2. Two hosts (keep separate)
| Host | Base | Used for |
|---|---|---|
| `halykmarket.kz` | `/gw` | token, order **list/detail**, product-by-order, **card create**, **photo upload** |
| `api.halykmarket.com` | `/api/merchant/v1` | order **state changes**, JSON:API relationship reads, **price/stock upload** |

---

## 3. ORDER INTAKE (pull orders → warehouse)

### 3.1 List new/all orders — `GET /gw/merchant/public/order/v2`
Query (all optional): `page`, `size`(≤100), `orderNumber`, `status`, `startDate`/`endDate`(`YYYY-MM-DD`).
No date range → last 3 months. Returns Spring page: `content[]`, `numberOfElements`, `hasNext`, `pageable`.
Each `content[i]` is a JSON:API `orders` object: `id`(internal), `attributes.code`(order number),
`status`, `totalPrice`, `deliveryMode`, `deliveryType`, `customer`, `addressLetterPath`(waybill URL),
`trackNumber`, `cancellationReason`, `relationships.entries`(line-items link).
> **No webhooks** observed — poll `?status=APPROVED_BY_BANK` on an interval for new orders.

### 3.2 Order detail — `GET /gw/merchant/public/order/v1?orderNumber=<code>`
One payload carries the **waybill**, the **Yandex courier OTP**, and **courier-service info**.

### 3.3 Line items / product mapping — `api.halykmarket.com`
- `GET /api/merchant/v1/orders/<id>/relationships/entries` → order lines
- `GET /api/merchant/v1/orderentries/<entryId>/relationships/product` → the shop product (→ your SKU)
- `GET /api/merchant/v1/orderentries/<entryId>/relationships/deliveryPointOfService` → pickup point
- `POST /gw/merchant/public/merchant/product/details-by-order` body `{"orderIds":[<int>…]}`
- **[open] scoping caveat:** `api.*` relationship endpoints returned a populated record for a
  placeholder id not belonging to us. **Do NOT enumerate order/entry ids**; only follow ids from
  your own order list.

### 3.4 Order status flow — `POST https://api.halykmarket.com/api/merchant/v1/orders`
Statuses: `APPROVED_BY_BANK`(new) → `ACCEPTED_BY_MERCHANT` → `WAITING_COURIER` → `COMPLETED`;
plus `CANCELLED` / `CANCEL_REQUESTED`. Every mutation is the same JSON:API envelope:
```json
{"data":{"type":"orders","id":"<internal id>","attributes":{"code":"<order number>","status":"<STATUS>"}}}
```
| Action | status | extra |
|---|---|---|
| Accept order | `ACCEPTED_BY_MERCHANT` | `countPlace`, `posCode` |
| Request HM courier | `WAITING_COURIER` | — |
| Send handover OTP to buyer | `COMPLETED` | headers `X-Security-Code:`(empty) + `X-Send-Code: true` |
| Complete (verify OTP) | `COMPLETED` | headers `X-Security-Code: <4 digits>` + `X-Send-Code: true` |
| Cancel | `CANCELLED` | `cancellationReason` |

Completion is 2-step: send OTP (texts buyer a 4-digit code) → buyer reads it back → complete with it.
Cancel allowed only in `APPROVED_BY_BANK`/`ACCEPTED_BY_MERCHANT`; `cancellationReason` ∈
`BUYER_CANCELLATION_BY_MERCHANT` / `BUYER_NOT_REACHABLE` / `MERCHANT_OUT_OF_STOCK`.

> **For warehouse sync:** on `MERCHANT_OUT_OF_STOCK` decrement; on new accepted order, decrement the
> ordered SKU qty in the warehouse and re-push stock (§4) so HM availability stays correct.

---

## 4. STOCK / PRICE PUSH (warehouse → HM)  ← the main sync

**Mechanism = price-list XML upload (FULL).** There is NO per-SKU stock endpoint that works for our
own cards (`save-and-map-sku` needs a skuId our cards don't expose). The price-list is the way.

### 4.1 Upload — `POST https://api.halykmarket.com/api/merchant/v1/offers/upload`
multipart `file=<xml>` → returns `{"id": <uploadId>}`.

### 4.2 Poll — `GET /api/merchant/v1/offers/upload/status/<id>`  (Content-Type: application/json)
Status flow **`CREATED → PROCESSING → COMPLETED | UPLOADED_WITH_ERRORS | FAILED`**.
⚠️ **CREATED and PROCESSING are BOTH non-terminal** — only stop on COMPLETED/UPLOADED_WITH_ERRORS/FAILED.
Terminal payload: `totalCount`, `successCount`, `notMappedCount`, `failCount`.

### 4.3 XML format (proven — one offer per SKU)
```xml
<?xml version="1.0" encoding="utf-8"?>
<merchant_offers date="YYYY-MM-DD" xmlns="halyk_market" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <company>Bricase KZ</company>
  <merchantid>000117600035</merchantid>
  <offers>
    <offer sku="<vendorCode>">
      <model><exact card name></model>
      <brand>No Name</brand>
      <barcodes><barcode><EAN></barcode></barcodes>
      <stocks><stock available="yes" storeId="Bricase KZ_pp1" isPP="yes" stockLevel="<qty>"/></stocks>
      <price><price int></price>
      <loanPeriod>3</loanPeriod>
    </offer>
  </offers>
</merchant_offers>
```
**Hard-won rules:**
- `sku` = the WB **vendorCode** = the card's **merchantProductCode** (1:1 mapping key).
- `loanPeriod` MUST be a real installment term (**3**/6/12/24). **`0` → `failCount`** (this was the
  whole "price never set" blocker).
- `storeId="Bricase KZ_pp1"` **with the space** (underscore fails); `isPP="yes"` (pickup point).
  Do NOT add `deliveryOptions` (a bad one → HTTP 400).
- `<price>` = regular price (integer, KZT). Sale price (акционная) is a separate cabinet step.
- **FULL upload** (`isIncremental:false` semantics): the file must contain **ALL** offers every time,
  else offers omitted may deactivate. Build one file with every SKU on each push.
- **`notMapped`** = card not yet indexed/approved (freshly created or still in moderation) — harmless,
  it maps on a later push once the card is live. `available="yes"` + `stockLevel=0` → shows
  «Нет в наличии» (correct for out-of-stock).
- **No per-offer error API** (tried `/upload/{id}`, `/errors`, `/report` → 404). Per-offer failures are
  visible only in the cabinet price-list report.
- **[ops] Stock must be refreshed ≥ every 90 days** or the card auto-archives. Run the sync
  periodically even if nothing changed.

### 4.4 Warehouse → offer field mapping (current implementation)
- **stock qty** ← warehouse "WB остаток" column (in the FBS export `stock.json`, **column index 12**).
  Keyed by SKU=vendorCode. Replace this source with the mp-warehouse live quantity per SKU.
- **price** ← WB discountedPrice (selling price) — swap for the warehouse/pricing source as needed.
- **barcode (EAN)** ← WB card `sizes[0].skus[0]`.
- **model** ← the exact HM card name (see `build_price.py` TITLE templates). Mapping keys on `sku`,
  so `model` need not be byte-exact, but keep it consistent.

Reference implementation to lift from: **`halyk/build_price.py`** (builds the 155-offer file) and the
upload+poll loop in **`halyk/finalize.py`** / `run_all.py`. Data snapshot in `halyk/data/`.

---

## 5. Gotchas the sync must handle
- **Token 429** → cache token (~2h TTL), refresh on expiry only.
- **Transient Halyk infra flaps** seen 2026-07-29: photo upload `minio-s3` DNS 409, offers/upload 500
  `AuthenticationServiceException`. These are **server-side**; retry with backoff, don't treat as our bug.
- **Poll terminal states correctly** (CREATED is non-terminal — see §4.2).
- **Don't enumerate ids** on `api.*` relationship endpoints (§3.3).
- Colour-variation **merge** is cabinet-only (Excel upload «Соединение вариаций товаров»); NOT in the
  merchant API — irrelevant to order/stock sync, just don't look for an API for it.

## 6. Warehouse-side trigger (user's intended flow)
User keeps FBS stock in a **Yandex.Disk `BRICASE KZ/WAREHOUSE`** folder, updated per HM order. Target
loop: HM order webhook/poll → decrement SKU in warehouse file → rebuild price-list (§4.3) → upload
(§4.1) → poll (§4.2). Yandex.Disk API creds live in the user's config (OAuth); egress to
`cloud-api.yandex.net` must be allowlisted in the environment network policy.
