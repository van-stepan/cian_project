# Halyk Market — merchant API (memory file)

Shared memory for the Halyk Market (Anyqtama) merchant API integration —
"Работа с заказами по API". Everything here has been read from the official docs and,
where marked, verified against the live production API from our shop.

Primary documentation:
<https://halyk-market.gitbook.io/anyqtama/massovye-operacii-i-integracii/rabota-s-zakazami-po-api>
(append `.md` to any GitBook page URL to get clean markdown; the full index is at
`https://halyk-market.gitbook.io/anyqtama/llms.txt`.)

Tags: **[live]** exercised against production and confirmed · **[confirmed]** read from
the docs · **[open]** still unknown.

---

## 1. Credentials

| Field | Value |
|---|---|
| `client_id` | `HMM_000117600035` |
| `client_secret` | in local `.env` / environment, never committed |
| BIN/IIN | `000117600035` |

**[live]** `client_id = HMM_ + BIN/IIN`. Our `HMM_000117600035` authenticates against
production. `client_secret` from the 27.07.2026 reset email (`api-noreply@halykmarket.com`)
is correct as transcribed from the screenshot — the earlier failure was request encoding,
not the secret. Still worth rotating eventually, since it has passed through a screenshot
and a chat.

Credentials load from `HALYK_*` environment variables (see §6), or a gitignored `.env`.
`.env.example` documents them.

---

## 2. Two hosts

The API is split across two hosts. The client keeps them separate (`gw_base` / `api_base`).

| Host | Base | Used for |
|---|---|---|
| `halykmarket.kz` | `/gw` | token, order **listing**, order **detail** (waybill / OTP / courier), product-by-order |
| `api.halykmarket.com` | `/api/merchant/v1` | order **state changes** + JSON:API relationship reads (entries, product, pickup point) |

**[open]** For the test environment the docs only name `test2.halykmarket.com/gw`; the
test host for the `api.*` surface is unconfirmed. Override with `HALYK_API_BASE` if needed.

---

## 3. Authorization — [live]

`POST https://halykmarket.kz/gw/auth/token`

**The body is JSON.** A form-encoded body returns **HTTP 500**, not 401 — this cost us a
debugging round. Send:

```json
{ "grant_type": "client_credentials",
  "client_id": "HMM_000117600035",
  "client_secret": "..." }
```

Response: `access_token` (JWT, ~128 chars), `token_type: "Bearer"`, `expires_in: 7199`
(~2 h). Use it as `Authorization: Bearer <token>` on every other call.

**[live] The token endpoint rate-limits (HTTP 429).** Requesting a fresh token on every
call trips it. The client therefore caches the token on disk
(`~/.cache/halyk_market/token-<hash>.json`, mode 600) and reuses it across CLI runs until
it expires. `--no-token-cache` disables it; `logout` clears it.

---

## 4. Reading orders

### 4.1 List — [live] `GET /gw/merchant/public/order/v2`

Query params (all optional): `page`, `size` (≤100), `orderNumber`, `status`,
`startDate` / `endDate` (`YYYY-MM-DD`). No date range → last 3 months.

Returns a Spring-style page: `content[]`, `numberOfElements`, `hasNext`, `pageable`, …
Each `content[i]` is a JSON:API `orders` object — `id` (internal), `attributes.code`
(order number), `status`, `totalPrice`, `deliveryMode`, `deliveryType`, `customer`,
`addressLetterPath` (waybill URL), `trackNumber`, `cancellationReason`, and a
`relationships.entries` link to the line items.

**[live] Our shop `HMM_000117600035` currently has 0 orders (all-time).** So end-to-end
listing is confirmed working, but no real order payload has been observed from our shop.

### 4.2 Order detail — [confirmed] `GET /gw/merchant/public/order/v1?orderNumber=<code>`

Same call backs three doc sections — the **waybill**, the **Yandex courier OTP**, and the
**courier-service info** are all fields on this one payload.

### 4.3 Line items / basket — [live] `api.halykmarket.com`

- `GET /api/merchant/v1/orders/<id>/relationships/entries` → order lines
- `GET /api/merchant/v1/orderentries/<entryId>/relationships/product` → the shop product
- `GET /api/merchant/v1/orderentries/<entryId>/relationships/deliveryPointOfService` → pickup point (self-collection)
- `GET /api/merchant/v1/pointofservices/<posId>/relationships/city`
- `POST /gw/merchant/public/merchant/product/details-by-order`, body `{"orderIds":[<int>...]}`

> **[open] — data-scoping caveat.** Calling `.../orders/11111111/relationships/entries`
> (the docs' placeholder id) with our token returned a **real, populated** order line
> (entry `12387686`, basePrice 322700) even though our shop has no orders. `11111111` is
> probably a shared sandbox record, but it may indicate the `api.*` relationship endpoints
> don't scope strictly to the calling merchant. **Do not enumerate order ids.** Flag to the
> account manager. We deliberately did not probe further.

---

## 5. Order status flow — [confirmed]

Statuses: `APPROVED_BY_BANK` (new, bank-confirmed) → `ACCEPTED_BY_MERCHANT` (accepted) →
`WAITING_COURIER` → `COMPLETED`; plus `CANCELLED` / `CANCEL_REQUESTED`.

Every mutation is the **same** call — `POST https://api.halykmarket.com/api/merchant/v1/orders`
with a JSON:API envelope — differing only by `status`, extra attributes, and headers:

```json
{ "data": { "type": "orders", "id": "<internal id>",
            "attributes": { "code": "<order number>", "status": "<STATUS>" } } }
```

| Action | status | extra | client method |
|---|---|---|---|
| Accept new order | `ACCEPTED_BY_MERCHANT` | `countPlace`, `posCode` (HM delivery) | `accept_order()` |
| Request HM courier | `WAITING_COURIER` | — | `request_courier()` |
| Send handover OTP to customer | `COMPLETED` | header `X-Security-Code:` *(empty)* + `X-Send-Code: true` | `send_customer_otp()` |
| Complete (verify OTP) | `COMPLETED` | header `X-Security-Code: <4 digits>` + `X-Send-Code: true` | `complete_order()` |
| Cancel | `CANCELLED` | `cancellationReason` | `cancel_order()` |

Completion is two steps: `send_customer_otp()` texts a 4-digit code to the buyer, then the
buyer reads it back and you pass it to `complete_order()`.

**Cancellation — [confirmed]** allowed only in `APPROVED_BY_BANK` or `ACCEPTED_BY_MERCHANT`
(before handover). `cancellationReason` ∈ `BUYER_CANCELLATION_BY_MERCHANT` (buyer refused),
`BUYER_NOT_REACHABLE`, `MERCHANT_OUT_OF_STOCK`. After cancelling, list queries for
`CANCELLED` orders include the `cancellationReason`.

**[open]** Pre-order mode ("режим предзаказа") and the delivery-mode-specific status graphs
(pickup / PVZ / postamat / sorting-center) are documented as diagrams we haven't captured.
Our shop's delivery mode isn't established yet — confirm before relying on a specific graph.

---

## 6. Usage

Set credentials as environment variables — best done once at the **environment level**
(claude.ai/code → environment settings → Environment variables) so every session inherits
them, since `.env` and the token cache die with each container:

```
HALYK_CLIENT_ID=HMM_000117600035
HALYK_CLIENT_SECRET=<from the reset email, no quotes>
HALYK_ENV=prod
```

Or locally: `cp .env.example .env` and fill it in.

```bash
python -m halyk_market.cli config                 # masked config, no network
python -m halyk_market.cli token                  # token (cached, reused)
python -m halyk_market.cli new --size 20          # orders awaiting acceptance
python -m halyk_market.cli orders --status COMPLETED --start-date 2026-01-01
python -m halyk_market.cli order 0008449018-1     # detail: waybill / OTP / courier
python -m halyk_market.cli entries 12345678       # line items

# state changes require --yes (they act on real customer orders):
python -m halyk_market.cli accept 11111111 1111111111-1 --yes
python -m halyk_market.cli courier 11111111 1111111111-1 --yes
python -m halyk_market.cli send-otp 11111111 1111111111-1 --yes
python -m halyk_market.cli complete 11111111 1111111111-1 4007 --yes
python -m halyk_market.cli cancel 11111111 1111111111-1 MERCHANT_OUT_OF_STOCK --yes

python -m halyk_market.cli raw GET /merchant/public/order/v2 --param size=5 --base gw
```

`-v` logs every HTTP call. From Python:

```python
from halyk_market import HalykMarketClient, OrderStatus
client = HalykMarketClient()
page = client.get_new_orders(size=50)
```

Requires `requests`. Offline tests (stub both hosts, no network):
`python halyk_market/tests_offline.py`.

---

## 7. Layout

```
halyk_market/
    config.py         credentials, two-host config, HMM_<BIN>, .env loading
    client.py         token handshake + on-disk cache, request layer,
                      all order read/mutate calls, status & reason constants
    cli.py            command line entry point
    tests_offline.py  stub-server test suite (17 checks)
.env.example          documented variables
.env                  real credentials, gitignored
```

Python 3, standalone from the Python 2 CIAN code in `main.py` / `support/`.

---

## 8. Environment note

`halykmarket.kz`, `api.halykmarket.com` and `halyk-market.gitbook.io` are reachable from
this sandbox **only after** the environment's network access was switched from **Trusted**
to **Custom** with those domains allowlisted (claude.ai/code → environment → Network access).
The block was never geographic — no proxy is involved. If a fresh session gets 403s to
these hosts, that setting was reset.

---

## 9. Product cards — creating listings [in progress]

Goal: mirror our Wildberries KZ catalogue onto Halyk, starting with the **C7** family.
Docs: "Загрузка товаров по API" / "Загрузка товаров без прайс-листа по API".

**[decided] Create genuinely new cards — never link to another seller's card.**
Halyk offers two upload routes; we use the first, not the second:

- ✅ **Create new** (`POST /gw/merchant/public/draft/product/moderation`) — build a fresh
  card from scratch and send it to moderation. **This is our path.**
- ❌ **Link/привязка** (`PUT /gw/merchant/public/product/remaining/save-and-map-sku`) —
  attach our stock/price to another seller's existing card. **Avoid.**

**[live] Create-new flow** (token from §3 authorizes all of these; read steps verified 200):
1. `GET /gw/merchant/public/skus/search?q=&page=&size=` — check the product isn't already listed.
2. `GET /gw/merchant/public/category/search?q=&page=&size=` — find the 3rd-level `categoryId`
   (categories expose `hasVariation`).
3. `GET /gw/merchant/public/brand/search?q=` — find `brand` id.
4. `GET /gw/merchant/public/form/product/feature?categoryId=<id>` — per-category attribute
   form (`attrs[]`, each with id/type/required; ENUM attrs list allowed values).
5. `POST /gw/merchant/public/file/image/upload/multiple` (multipart `files=@...`) — upload
   photos, returns media `{id, link}`.
6. `POST /gw/merchant/public/draft/product/moderation` — submit: name, category, brand,
   description, `attrs[]`, `media[]`, weight/width/height/depth,
   `info{ merchantProductCode, pointByCity[], loanPeriod }`. Returns `{id, productDraftStatus:"CHECK"}`.
7. `GET /gw/merchant/public/draft/product/<id>` — poll moderation status.

**[open] WB-style variation grouping.** The moderation payload is a **flat single card** —
no "parent"/variation-group field the merchant sets. Halyk's catalogue does have variations
(`hasVariation:true`, `sku-variations` in image paths), but grouping separate colour SKUs
into one card with a colour switcher appears to be **catalogue-side matching**, not merchant-
controlled via this API. So "join colours into one card like WB" may not be achievable through
the API as-is. Confirm the intended mechanism with the account manager before relying on it.

**[live] Wildberries source — working.** WB KZ (mag1) Supplier token is in gitignored `.env`
as `WB_KZ_TOKEN` (expires 2026-12-21). Requires the WB hosts to be allowlisted in the env's
Custom network policy: `*.wildberries.ru`, `*.wb.ru`, `*.wbbasket.ru`, `*.wbstatic.net`.
Content API: `POST https://content-api.wildberries.ru/content/v2/get/cards/list`
(header `Authorization: <token>`, no "Bearer"), body
`{"settings":{"cursor":{"limit":100},"filter":{"withPhoto":-1}}}`, paginate on
`cursor.updatedAt`+`nmID`.

**[live] SKU / family convention (confirmed against real vendorCodes):**
`<caseType>-<phonemodel>-parent-<colorToken>`, e.g. `c7-iphone-17promax-parent-col8`.
- **family = substring before `-parent-`** (`c7-iphone-17promax`) — the grouping key.
- colour token after `-parent-` (`col8`) is internal; the real colour name is the WB
  characteristic **"Цвет"** (col8 → синий/blue). All colours of a family share WB `imtID`.
- **C7 inventory:** 14 families, 37 SKUs (e.g. `c7-iphone-17promax` and `c7-iphone-17pro`
  have 7 colours each; samsung families 1–4 each).

**[live] WB→Halyk mapping (first card, `c7-iphone-17promax-parent-col8`, nm 1257637259):**
- category `20004` "Чехлы для смартфонов" (3rd level) · brand **Bricase — NOT on Halyk**
- required attrs resolved: Тип[10070]=Накладка(36472), Материал[10078]=Пластик(12398);
  plus Совместимость[10081]=Apple iPhone 17 Pro Max(1289567), Цвет[10068]=Синий(12801),
  Вес[10067]=50. Values sent as `classAttrValueId` (confirm id-vs-name on first submit).
- 8 photos on `basket-44.wbbasket.ru` as `.webp` (download + likely convert to jpg/png for
  Halyk's `/file/image/upload/multiple`). Barcode (WB skus[0]) = 2048234005949.

**[resolved] Brand → no-brand.** Bricase is not on Halyk and there is **no brand-create API**
(search-only; swagger locked; Halyk requires a trademark cert to add a brand — content-team
action). Decision: use **«Без бренда» = brand id `33006`** (also available: Noname 112117,
No Name 10721, Generic 25258, Unbranded 106083). To carry the Bricase identity later, ask the
account manager to register it.

**[resolved] Price → from WB KZ.** `GET https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter?limit=1000`
(header `Authorization: <token>`), match `listGoods[].nmID`. First card
`c7-iphone-17promax` family: **base 15088 / discounted 6035.2 KZT**. Decide base-vs-discounted
and any Halyk-commission markup before submit.

**[resolved] Photos.** Use the **`big`** size, not `hq` (WB CDN 404s on `hq`). Download webp
from `basket-44.wbbasket.ru`, convert to JPEG (Pillow), then `POST /file/image/upload/multiple`.

**[BLOCKER — needs Halyk cabinet]** `info.pointByCity` still needs: **warehouse point code**
(`posName` of a PoS created via `POST api.halykmarket.com/api/merchant/v1/pointofservices/save`),
**city code** (e.g. 750000000 = Almaty), and **stock amount**. There is no list-GET for points
(`/pointofservices` → 404), and WB can't supply a Halyk point code. If the shop has no PoS yet,
one must be created first. Confirm Halyk dimension units (WB gives cm + kg) on first submit.

**[open] WB-style colour grouping — still not merchant-controllable via the create API.** On
WB the colours are separate `nmID` cards grouped by `imtID`; Halyk's create API takes one flat
card with a single Цвет. Grouping colours into one Halyk card appears catalogue-side. Confirm
the mechanism with the account manager before promising WB-style variation cards.

**[live ✅] FIRST CARD SUBMITTED — validated recipe.**
`c7-iphone-17promax-parent-col8` → Halyk draft **id 635083**, `productDraftStatus: CHECK`
(submitted 2026-07-28; awaiting moderation, no comment yet). Working end-to-end recipe:
1. **Upload photos** `POST /gw/merchant/public/file/image/upload/multiple`, multipart field
   `files=` (JPEG). Response is a list; each item has `id` + `assetUrl`. Build
   `media=[{"id":<id>,"link":<assetUrl>}]`.
2. **Submit** `POST /gw/merchant/public/draft/product/moderation` → **HTTP 202**
   `{"productDraftStatus":"CHECK","id":<draftId>}`.
   - **attrs accepted as NAMES** (`"Накладка"`,`"Пластик"`,`"Apple iPhone 17 Pro Max"`,`"Синий"`,
     `"Apple"`,`"MagSafe"`, vendorCode, `"50"`) — the id fallback was not needed.
   - dimensions sent as **strings** (`"50","9","18","2"`); price int `6035`; stock int.
   - `info.pointByCity[0]` = city `750000000`/Almaty, point `Bricase KZ_pp1`, amount = stock.
3. **Poll** `GET /gw/merchant/public/draft/product/<draftId>`.

**Stock decision:** user chose to mirror **«WB остаток» = 20** (not «Доступно» = 3);
oversell risk acknowledged. Stock file `FBS_STOCK_BRICASE_KZ.xlsx`, sheet `СКЛАД`, key column
`SKU`, values `Доступно для заказа` / `WB остаток`. All 37 C7 SKUs are present in it.

**[fixed] Name & price corrections (learned from rejections):**
- **Name** must be `Тип + Модель + отличительные характеристики` incl. material; the first
  name "Дизайнерский чехол для IPHONE 17 PRO MAX" was REJECTED («Несоответствующее описание»).
  Working title template: **`Чехол для iPhone 17 Pro Max <color> из пластика с металлической
  камерой-подставкой и MagSafe`** (`<color>` = WB "Цвет" primary value, e.g. серый).
- **Price is two fields.** Map WB `price` → Halyk `pointByCity.price` (regular, struck-through)
  and WB `discountedPrice` → **`pointByCity.salePrice`** (the field first left null). First card
  wrongly put 6035 alone in `price`. Correct: price=15088, salePrice=6035 (WB club price dropped).

**[limitation] A REJECTED draft cannot be fixed via API.** `/draft/product/{id}` allows only
GET/DELETE (no PUT/PATCH); DELETE returns «Нельзя удалять товар в модерации» (REJECT counts as
in-moderation); a fresh POST hits `draft_with_product_code_already_exists`. So editing/deleting a
rejected draft is **cabinet-only**. Practical path: create a fresh sibling SKU instead, or delete
the bad draft in the cabinet then recreate via API.

**[live] Cards created:**
- 635083 `...-col8` — REJECTED (bad name), stuck (cabinet-delete needed).
- 635092 `...-col7` «Чехол для iPhone 17 Pro Max серый …» — price 15088/6035, stock 20,
  status MODERATION (progressing). Recipe validated with corrected name + price.

**[open] Colour grouping:** the draft has a `draftVariations` field (structure TBD) — likely the
real lever to join colours into one card with a selector. Investigate before the family batch.

**[requirement] Photos must be 1:1 square on white.** Halyk photo rules: equal width/height
(**square 1:1**), min 500×500, max 2000×2000, **white background**, JPEG/JPG ≤2 MB, ≥3 photos.
WB images are **900×1200 (3:4)** and photos **1–2 are coloured marketing renders**; photos
**3–8 are on white** (≥6 compliant per card). Pipeline: detect white-bg shots by corner
sampling (min(corner RGB) > ~238), drop the renders, **pad each to 1200×1200 white square**,
save JPEG q90. Both first cards used the raw 3:4 renders → non-compliant; 635092 will likely
reject on photos despite correct name/price.

**[process] Submit each SKU ONCE with the complete recipe.** Because a rejected draft is locked
(cabinet-only to fix), get name + price(two fields) + square-white photos all correct before the
single POST. 635083 and (probably) 635092 need cabinet deletion.

**[live] Cards so far:**
- 635083 col8 — REJECT (name), stuck (cabinet-delete).
- 635092 col7 — 3:4 coloured photos, MODERATION (photo-strictness test; no verdict yet).
- **635432 col6 «…голубой…» — full correct recipe** (template name + 15088/6035 + 6 white-bg
  photos padded to 1200×1200 square). MODERATION, progressing. This is the validation card.

Image display: Halyk stores the uploaded master as-is (assetLarge/assetThumbnail point to the
same file) and only scales for display — it does NOT reshape aspect ratio or add white bg, so
compliant 1:1 white uploads are required; the "resize" seen in the cabinet is display scaling.

**[critical] Fill ALL 14 category characteristics — completeness must be ~100%.** The API marks
only 3 attrs `required` (Тип 10070, Материал 10078, Модель 51833) but moderation rejects
«заполнить обязательные поля характеристик до 100%» unless ALL 14 attrs of cat 20004 are filled.
The 6 easily missed + values used for the case line:
- 287521 Код NTIN = barcode (EAN from WB skus[0])
- 35427 Дополнительно = "Защита камеры, дополнительная угловая защита бортов телефона" (valid opt)
- 10065 Размер = "iPhone 17 Pro Max"
- 51838 Текстура чехла = "Тканевая"
- 40097 Товары из Турции = "false" (BOOLEAN)
- 35425 Защита = "Защита камеры и экрана"
Also: Особенности 10064 must be a valid option — use **"Поддержка magsafe"**, NOT "MagSafe".

**[finding] Photos were NOT the blocker.** col7 (3:4 coloured photos, 8 attrs) rejected with the
SAME completeness message as col6 — Halyk did not complain about the 3:4/colour images. Keep
uploading square-white anyway (spec + catalogue tiles), but completeness is the real gate.

**[live] Cards:** 636519 col4 «…сиреневый…» — **all 14 attrs + square-white photos + 15088/6035**
— MODERATION, the true validation card. REJECTED/stuck (cabinet-delete to reuse codes): 635083
col8 (name), 635432 col6 (attrs), 635092 col7 (attrs). Fresh codes left in family: col2, col11, col14.

**Next:** await 636519 verdict. If it passes, the full recipe (name schema + all-14 attrs +
two-field price + square-white photos) is proven — then batch remaining SKUs and have the cabinet
clear the 3 stuck drafts so col6/7/8 can be recreated.
