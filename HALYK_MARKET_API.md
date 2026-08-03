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

**[critical fix] ENUM attribute values MUST be the numeric `classAttrValueId`, not the name.**
Names ARE stored but don't register as a valid selection, so required ENUM fields (Тип 10070,
Материал 10078) read as empty → rejection «заполнить обязательные поля до 100%». col4 (636519,
all 14 attrs as NAMES) → REJECT; col2 (636546, ENUM as IDs) → testing.
- ENUM value IDs: Тип Накладка=**36472**, Материал Пластик=**12398**, Совместимость
  Apple iPhone 17 Pro Max=**1289567** (get others from the form's `classAttrValueId`).
- STRING attrs keep text values. Код NTIN (287521) rejects the EAN barcode (stores empty) — omit.
- So a passing attrs list needs: ENUM→id, STRING→text, NUMBER→"50", BOOLEAN→"false", covering
  the ~13 fillable attrs of cat 20004.

**[live] Cards:** 636546 col2 «…зеленый…» ENUM-as-IDs = current validation card (MODERATION).
Burned/stuck (cabinet-delete to reuse): 635083 col8, 635432 col6, 635092 col7, 636519 col4.
Fresh codes left in family: col11, col14.

**[✅ RECIPE PROVEN] 636546 col2 passed moderation → status SUCCESS (live).** The full validated
recipe: name template `Чехол для <model> <color> из пластика с металлической камерой-подставкой и
MagSafe`; brand 33006; ALL 13 fillable attrs with **ENUM values as option IDs** (Тип 36472,
Материал 12398, Совместимость <per-model id>), STRING as text, Цвет as name, Вес "50", BOOLEAN
"false"; two-field price (price + salePrice); ≥3 white-bg photos padded to 1200×1200 square.

**[✅ FULL C7 BATCH SUBMITTED]** All 37 C7 SKUs handled. Batch script: `batch_rest.py` (derives
compat option ID from the vendorCode model, not the messy WB Совместимость char; auto-resolves
colour/price/stock/photos; validates before POST).
- **col2 iphone-17promax = SUCCESS (live).**
- **32 fresh SKUs submitted → MODERATION** (drafts 637264-637301): iphone-17promax col11/14;
  iphone 14/15/16 promax; iphone 17; iphone 17pro (7 colours); samsung s23/s23fe/s23ultra/s24/
  s24fe/s24ultra/s25/s25ultra families.
- **4 stuck (need cabinet delete):** iphone-17promax col4 (636519), col6 (635432), col7 (635092),
  col8 (635083) — rejected during the recipe-discovery iterations; API can't delete/edit them.

**[open] cosmetics:** Samsung "FE" titles render as "…S24 Fe" (a `.title()` lowercasing) — compat
attr ID is correct; only the title text is slightly off. Fix on any re-run.

**[live] C7 iphone-17promax family fully resubmitted:** col4/6/7/8 recreated after cabinet
delete (637378/380/381/382), joining col2(SUCCESS)/col11(637264)/col14(637265).

**[recipe per case type]** Same base recipe, differing by title + Материал(ENUM id) + Особенности:
- **C7**: «Чехол для <m> <c> из пластика с металлической камерой-подставкой и MagSafe» · Пластик(12398) · Поддержка magsafe
- **C10**: «Дизайнерский чехол для <m> <c> из пластика с MagSafe и защитой камеры» · Пластик(12398) · Поддержка magsafe
- **C6**: «Мягкий тканевый чехол для <m> <c> с soft-touch покрытием и защитой камеры» · Ткань(13035) · Покрытие soft-touch
- **C5**: «Кожаный чехол для <m> <c> с кольцом-подставкой и поддержкой беспроводной зарядки» · Искусственная кожа(11610) · Поддержка беспроводной зарядки
- **C2**: «Чехол с кольцом-подставкой для <m> <c> из пластика с защитой камеры» · Пластик(12398) · Кольцо-держатель
Материал ids: пластик 12398, искусственная кожа 11610, ткань 13035, экокожа 13343, силикон 12795.
Type test cards: C2 637375, C10 637376, C5 637383, C6 637384 (all MODERATION).

**[fix] Photos:** prefer white-bg squared, but if <3 white (e.g. C5 leather has only 2), fall back
to padding other photos to square to reach ≥3. Halyk is lenient on photos (col7 with 3:4 coloured
shots rejected on characteristics, not photos), so count matters more than pure white.

**[compat resolver]** match WB Совместимость char values against Halyk options first; fallback to a
name constructed from the vendorCode model (iphone-17pro → "apple iphone 17 pro").

**[MERGE / colour grouping — hypothesis, unverified]** No explicit merge API; docs silent;
approved col2 has `draftVariations: null`. Best hypothesis: **Модель/Артикул производителя [51833]
is the grouping key** — cards sharing the same value group into one card with a colour selector,
Цвет as the variant axis. Our cards currently set [51833] = the UNIQUE full vendorCode, so they
will NOT group. To enable grouping, set [51833] = the family base (e.g. "c7-iphone-17promax") shared
across colours, keeping merchantProductCode unique. Needs testing on one family OR account-manager
confirmation; merging can only take effect after approval.

**[❌ GROUPING VERDICT: shared-Модель does NOT group]** User confirmed in Товары: the 5
`c10-iphone-17pro` colours (all sharing «Модель/Артикул» = `c10-iphone-17pro`) appear as **5
separate, unconnected entries**. So sharing the Модель field does NOT merge colours. Merging
colours into one colour-selector card is **not merchant-API-controllable** — no create-API field
does it. Options: **account-manager / Qoldau request**, or price-list XML parent (unverified).
Keep per-colour cards; do NOT recreate families for grouping.

**[✅ C10 recipe validated]** C10 type test 637376 → SUCCESS. All 5 grouping-test cards
637386-390 → SUCCESS. Note: moderation **remaps brand 33006 → 10721 (No Name)** on approval.
**[grouping verdict pending manual storefront check]** — merchant API exposes no live-product URL,
no grouping field (draftVariations stays null post-approval), and the storefront product API is
auth-locked; so grouping can only be confirmed by looking at halykmarket.kz. Ask user: do the 5
c10-iphone-17pro colours show as ONE colour-selector card or 5 separate cards?

**[GROUPING TEST live]** Created the full **c10-iphone-17pro** family (5 colours, drafts 637386-390:
Чёрный/Тёмно-синий/Тёмно-зелёный/Тёмно-бордовый/Сиреневый) all with **shared Модель/Артикул [51833]
= `c10-iphone-17pro`** (merchantProductCode still unique per colour). Hypothesis: after approval
these collapse into ONE card with a colour selector. **Verdict pending moderation** — when they
reach SUCCESS, check the storefront: if one product page with a colour switcher → shared-Модель is
the grouping key (apply everywhere, re-create earlier families with shared Модель); if 5 separate
cards → hypothesis wrong, ask account manager.

**[limitation] No card-EDIT API.** Per "Просмотр и изменение карточек": editing a card's fields
(incl. Модель/Артикул) is a **manual request to Halyk Qoldau partner support** — there is no
update/PUT endpoint; the merchant API only creates. Re-POSTing a merchantProductCode = 400
already_exists. So to change Модель on existing cards: either **recreate via API** (delete+create)
or **file a Qoldau support request**. For ~90 cards, recreate is the faster self-service path.

**[verified] Delete/recreate cycle:** cabinet-deleted rejected drafts return 404 (truly gone) and
the API recreates them with the SAME merchantProductCode (proven: col4/6/7/8 old 635083/635432/
635092/636519 → 404, new 637378/380/381/382 live). **But the API cannot delete an APPROVED card** —
DELETE /draft/product/<id> on the live col2 (636546, SUCCESS) returned 404 and the card stayed live.
So deleting an approved card is **cabinet-only**; the API can then recreate once the code is freed.

**[BLOCKER - price/stock not set] Cards approve with content but 0 price/stock.** The moderation
payload's `info.pointByCity` price/stock does NOT propagate to the live offer; price/stock is a
SEPARATE post-approval step. Warehouse `Bricase KZ_pp1` (Алматы, active) is CORRECT — not the
issue.
- `PUT /product/remaining/save-and-map-sku` needs a **skuId** ("The given id must not be null");
  our own cards are NOT returned by `skus/search` (0 results even by our product code), so we
  can't get their skuId → this endpoint is only for the привязка/map flow, not own cards.
- **✅ SOLVED — price-list XML sets price/stock; the bug was `loanPeriod=0`.** `POST
  api.halykmarket.com/api/merchant/v1/offers/upload` (multipart `file`) → `{id}`; poll
  `GET .../offers/upload/status/<id>` for `status` + success/notMapped/fail counts.
  **WORKING offer XML** (`success=1` for `c10-iphone-17pro-parent-black`):
  ```xml
  <merchant_offers date="YYYY-MM-DD" xmlns="halyk_market">
    <company>Bricase KZ</company><merchantid>000117600035</merchantid>
    <offers><offer sku="<vendorCode>">
      <model><exact card name></model><brand>No Name</brand>
      <barcodes><barcode><ean></barcode></barcodes>
      <stocks><stock available="yes" storeId="Bricase KZ_pp1" isPP="yes" stockLevel="<qty>"/></stocks>
      <price><regular price></price>
      <loanPeriod>3</loanPeriod>   <!-- MUST be a real term (3/6/12/24); 0 => fail=1 -->
    </offer></offers></merchant_offers>
  ```
  - `loanPeriod` MUST be ≥3 (installment term); **0 causes fail=1** (this was the whole blocker).
  - `storeId="Bricase KZ_pp1"` WITH the space is correct (underscore fails). `isPP="yes"` (it's a
    pickup point). `deliveryOptions` NOT needed (a bad one gives HTTP 400 on upload).
  - `<price>` = REGULAR price. Sale price (акционная) is a SEPARATE step (Добавление акционной цены).
  - Upload type is FULL (`isIncremental:false`) → the file should contain ALL offers, else offers
    not listed may deactivate. Build one file with every SKU.
- User's ongoing plan: FBS stock file on Yandex.Disk updated per order → build that file → price-list
  XML (this format) → upload. That's the stock sync.

**[ops] Stock must be refreshed ≥ every 90 days** or the card auto-archives. Halyk does not manage
prices/stocks — the seller keeps them current (our WB-остаток sync will need to run periodically).

**Next:** await verdicts on (a) grouping test 637386-390, (b) the 4 type tests (C2 637375, C10
637376, C5 637383, C6 637384). Then: if grouping works, re-create families with shared Модель (no
edit API) and batch remaining C5/C6/C10 with it; else batch as per-colour cards. C5/C6/C10 full
batch HELD until a type test of each passes.

---

## 2026-07-29 — full-catalogue expansion + Halyk infra outage

**[✅ ALL type tests SUCCESS]** GET `/gw/merchant/public/draft/product/<id>` returns
`{productDraftResponse:{…,status}, comment}` — status lives at `productDraftResponse.status`
(NOT `productDraftStatus`), `comment` holds the rejection reason. Confirmed SUCCESS:
C2 637375, C5 637383, C6 637384, C10 637376, C7 col2 636546, grouping 637386. So the whole
C-series recipe (base + per-type Материал/Особенности table above) is fully validated.

**[catalogue taxonomy]** WB has **155** cards. By vendorCode prefix / case type:
- `c7` 37, `c10` 21, `c6` 6, `c5` 4, `c2` 1  — C-series (recipe validated).
- `b1`/`b2`/`b3`/`b5` = **22** → all *«Чехол-книжка из кожи»* = **book-leather** (new type).
- phone-brand-named (`google/honor/huawei/oneplus/realme/samsung/tecno/xiaomi/redminote…`) = **64**
  → all *«Мягкий Soft Touch чехол»* = **soft-touch** (new type). One case type, many models.

**[new-type recipes — same base, differ by title + Тип[10070] + Материал[10078] + Особенности[10064]]**
- **soft-touch**: Тип Накладка(36472) · Материал Силикон(12795) · Особенности «Покрытие soft-touch» ·
  текстура(51838) «Силиконовая» · title «Чехол Soft Touch для <m> <c> из силикона с защитой камеры».
- **book-leather**: Тип «Чехол книжка»(13288) · Материал Экокожа(13343) · Особенности «Отделение для
  банковских карт» · текстура «Кожаная» · title «Чехол-книжка для <m> <c> из экокожи с отделением для карт и подставкой».
- More ENUM ids (from the form): Тип «Чехол с подставкой»=667931 (used for C5/C2), «Чехол книжка»=13288,
  Чехол-накладка=13287; Материал Силикон=12795, Экокожа=13343, Кожа=15971, Искусственная кожа=11610.
- Особенности[10064] valid option NAMES: «Покрытие soft-touch», «Отделение для банковских карт»,
  «Кольцо-держатель», «Поддержка беспроводной зарядки», «Поддержка magsafe» (pass NAME, not id — only
  Тип/Материал/Совместимость need numeric ids).

**[compat catalogue GAP — key constraint]** Совместимость[10081] has **231** options and is
`required=False`. Many WB models are **absent** from it: NO Google Pixel, NO OnePlus, NO Tecno Camon 40,
NO Xiaomi 17/12 Pro/11T Pro, NO Realme 11/14/15, NO Samsung S21(plain)/M31. Coverage of remaining work:
soft-touch **47 of 64** miss compat, book **5 of 22** miss compat. General resolver = normalise WB
Совместимость values and match the catalogue (first hit); else iPhone/Samsung constructor from
vendorCode; else **omit 10081** (it's optional). OPEN: does omitting compat drop completeness below the
~100% moderation gate? → test card `google-pixel7-parent-black` (no compat) will answer empirically. If
it rejects, fallback = compat «Универсальный» (last catalogue option) to keep the field filled.

**[colour alias]** 6 "fuchsia" cards have WB Цвет `['ярко-розовый','фуксия','розовый неон']`, none in
Halyk's 64 colours → alias to **Малиновый**. Resolver: exact match first, then COLOR_ALIAS fallback.

**[⚠️ HALYK INFRA OUTAGE 2026-07-29 ~17:00Z — transient, NOT our bug]** Two Halyk upload backends
down simultaneously:
- **Photo upload** `POST /gw/merchant/public/file/image/upload/multiple` → **HTTP 409** `"minio-s3.halykmarket.com:
  Temporary failure in name resolution"` (their object store's DNS is broken).
- **Price/stock** `POST api.halykmarket.com/api/merchant/v1/offers/upload` → **HTTP 500**
  `org.springframework.security.authentication…` (their token-introspection backend flapping).
- Token, moderation submit, and all GET/read endpoints are UP; our token verifies (gw GET 200). Both
  failures are server-side. Card creation NEEDS photos → fully blocked until minio recovers.

**[tooling]** `scratchpad/batch_all.py <mode>` — one idempotent creator for every case type (modes:
`creminder` = C10/C5/C6/C2 remainders, `tests` = 3 new-type probes, `softtouch`, `book`, or a single
sku). General compat/colour/model/maker resolvers; white-bg square photos (≥3, fallback to any);
`already_exists`→ALREADY. `scratchpad/orchestrate.py` (bg task) polls minio+offers every 60s for ~90 min
and, on recovery, runs `creminder`+`tests` then pushes the price-list; writes `ORCH_STATUS.json`.

**Next once infra recovers:** (1) orchestrate.py creates C10/C5/C6/C2 remainders (~23) + 3 new-type
tests, and pushes price/stock for the ~46 existing offers. (2) When soft-touch & book tests reach
SUCCESS, run `batch_all.py softtouch` (64) and `batch_all.py book` (22). (3) Rebuild price_all.xml to
cover EVERY created SKU (full upload) and re-push.

**[✅ EXECUTED — infra recovered ~17:25Z]**
- **Price/stock upload: total=46 success=46 fail=0** — the 46 existing cards now have price+stock
  (WB discountedPrice, WB-остаток qty, loanPeriod=3). They should flip to В продаже / un-archive.
- **C10/C5/C6/C2 remainders created: 23/23** → drafts **638598–638623** (all MODERATION).
- **New-type test cards created (MODERATION):** soft-touch+compat `638619` (Samsung S23),
  soft-touch NO-compat `638620` (Google Pixel 7 — the completeness probe), book-leather `638623`
  (Samsung A54). Transient 503/504 photo-upload hiccups on 3 SKUs were retried → all OK.
- **`scratchpad/finalize.py` (bg)** polls those 3 test drafts every 180s (≤4h); on verdicts it
  auto-runs `book`(22) if book=SUCCESS and `softtouch`(64) if soft-touch tests pass — using the
  **Универсальный** compat fallback (env `SOFTTOUCH_UNIVERSAL=1`) IF the no-compat probe (638620)
  REJECTS but the with-compat one (638619) passes — then rebuilds the full 155-offer price-list and
  re-pushes. Verdicts + counts land in `FINAL_STATUS.json`.
- Model-name casing cleaned (connectors и/с/для lowercased; FE/SE/5G kept upper; Pro/Max/Ultra
  Title-cased) in both `batch_all.py` and `build_price.py`.

---

## 2026-07-30 — FULL CATALOGUE LIVE (155/155 cards) + compat near-match fix

**[✅ ALL 3 new-type tests SUCCESS incl. no-compat probe]** 638619 (soft-touch+compat), 638620
(soft-touch NO-compat Pixel 7), 638623 (book) all reached SUCCESS. **Blank Совместимость does NOT
fail the completeness gate** → soft-touch models absent from the catalogue are created with compat
omitted (no «Универсальный» needed). The 23 C-remainders (638598-618) all SUCCESS too.

**[✅ EXPANSION DONE]** `batch_all.py softtouch` → 64/64, `batch_all.py book` → 22/22 (1 transient
502 retried → OK, e.g. tecno-camon40pro-siren 639420). **Every one of the 155 WB SKUs now has a
Halyk card** (37 C7 + 21 C10 + 6 C6 + 4 C5 + 1 C2 + 22 book + 64 soft-touch = 155).

**[compat resolver — safe near-match added]** `variants()` now relaxes ONLY same-body differences:
strip network band `\b[45]g\b`, and prefix `xiaomi ` for Redmi/Poco (the catalogue writes
"Xiaomi Redmi Note…"). Recovered 6 cards (Redmi Note 12/13 Pro 5G, Xiaomi Mi 11 Lite, Tecno Camon
20 Pro 5G). Never relaxes model-defining tokens — S21 is NOT mapped to S21 FE. Blank-compat now
soft-touch **43**/book **3**.

**[⚠️ COMPAT CATALOGUE GAP — needs Qoldau request]** 46 cards across ~23 models are absent from
Halyk's 231-model Совместимость enum (no API/draft way to add): Google Pixel 7/7Pro/8, OnePlus 11,
Samsung S21/S21 Ultra/M31, Realme 11 Pro/14 Pro+/15 Pro/15T/9 Pro+/9 5G, Tecno Camon 40/40 Pro,
Xiaomi 17/11T Pro, Honor 10X Lite/400 Pro, Huawei Nova 8i. These are created with the model in the
title + Модель attr but no structured phone-filter. Only fix = ask Halyk/Qoldau to add them to the
catalogue, then re-tag (recreate, no edit API).

**[price/stock — FULL 155-offer upload]** `build_price.py` builds all 155; upload status flow is
**CREATED → PROCESSING → COMPLETED/UPLOADED_WITH_ERRORS** (poll must treat CREATED as non-terminal;
only stop on COMPLETED/UPLOADED_WITH_ERRORS/FAILED). Latest: **success=94, notMapped=59, fail=2**.
notMapped = the 86 freshly-created cards not yet indexed (map once moderation approves them → re-push
periodically). **No API endpoint exposes per-offer errors** (tried /upload/{id}, /errors, /report,
/offers → 404); the 2 fails are visible only in the cabinet price-list report.

**[ops] Routine `trig_01EKdHiGvHuyk5SE2wyQ3vV1`** repurposed to a periodic price re-sync: rebuild +
re-push `price_all.xml` so newly-approved cards flip to В продаже; self-deletes once notMapped→~0.
(Deleted 2026-07-30 after re-sync reached success=153 / notMapped=0.)

**[stock] «Нет в наличии» = WB остаток 0, NOT an error.** Cabinet Товары split (98 В продаже /
57 Нет в наличии) matches our data: **58 of 155 SKUs have WB-остаток 0**. Those show as out-of-stock
(correct); they flip to В продаже automatically when WB restocks and the price-list is re-pushed. The
earlier "fail=2" in the offer upload is negligible/rounding, not a findable cabinet error.

---

## 2026-07-30 — live-data rule, real order, photo aspect

**[RULE] ALWAYS re-check orders & live stock against Halyk live — never trust a cached note.**
(A stale "0 orders" note was wrong.) Query `GET /gw/merchant/public/order/v2` (no params → 400 on
some param combos; bare call works) every time orders/stock come up.

**[live] 1 real order** `0013597323-1`, status `DELIVERY_PVZ` (СДЕК → Almaty PVZ), 5281 ₸, SKU
**`c7-samsung-s23ultra-parent-col7`** (standalone card). **Exclude this SKU from any delete/recreate.**

**[photos] Square was over-cautious — Halyk displays cases portrait 3:4.** Cabinet photo frames are
3:4; WB images are native 900×1200 (3:4) with `photos[0]` = colourful marketing cover (frame+text).
`batch_all.py` photo step changed to upload **native WB images in WB order, no square/white padding**
(WB cover → Halyk «Обложка карточки»). Applies to future/recreated cards. **No photo-edit API** → to
fix existing cards = delete (cabinet-only) + recreate + re-price + re-merge. Plan: **pilot 1 standalone
card** (`b3-samsung-s24ultra-parent-red`) → recreate → verify → then the other 153 no-order cards.

## 2026-07-30 — ✅ COLOUR GROUPING SOLVED via cabinet «Соединение вариаций товаров»

**Supersedes the earlier "grouping not API-controllable / account-manager only" verdict.** The
Halyk **Partners cabinet** has *Товары → Добавление товара → Объединение товаров → Вариации товара →
Соединить* ("Соединение вариаций товаров") — an **Excel/XML template upload** that merges cards into
ONE storefront product with a colour selector.

**Template** («Скачать шаблон» for category Чехлы для смартфонов) has 2 sheets:
- `Товары для объединения`: columns **`sku` | `name` | `Код вариации` | `Цвет`**. Cards sharing the
  same **Код вариации** merge into one product; **Цвет** (from the allowed list) is the selector axis.
- `значения`: **41 allowed Цвет values** — DIFFERENT vocab from the card-creation Цвет(64): here it's
  Бежевый…Фуксия…Мультиколор…Черный (has Фуксия & Мультиколор; NO Малиновый/Графитовый/Золотой →
  map Малиновый→Фуксия, Графитовый→Темно-серый, Золотой→Золотистый, Темно-бордовый→Бордовый, etc.).

**[builder] `halyk/build_merge.py`** groups our 155 cards by family (`sku` minus `-parent-<colour>`),
keeps only multi-colour families (**37 families / 110 cards**), sets Код вариации = family slug, maps
each card's colour to the 41-value merge vocab (0 within-family collisions), names via the same
creation TITLE templates → writes `merge_filled.xlsx`. 45 single-colour models stay standalone →
storefront goes **155 cards → 82 products**.

**[⚠️ merge is CABINET-ONLY — no API]** POSTing the file to every plausible merchant-API path
(`gw/merchant/public/product/variation/upload`, …) returns Spring **"No static resource"** / 404 —
the feature is NOT in the merchant-API namespace; it lives behind the **cabinet's own login**
(separate auth from our client_credentials; bank-grade, SMS/OTP). So the merge file must be uploaded
**manually in the cabinet** (or via a browser driven with the user's cabinet session cookie). Our API
token cannot do it. **2026-07-30 12:37: user uploaded `merge_filled.xlsx` in the cabinet → ✅ «Завершено. Успешно: 37,
Частично: 0, Пропущено: 0, В ошибке: 0».** All 37 colour families merged cleanly into single
colour-selector products. Storefront is now 82 products (45 single + 37 merged). Colour grouping is
DONE — repeat this flow (build_merge.py → cabinet upload) whenever new colours are added.

**[✅ the "2 fails" identified & fixed] Duplicate product name in the price-list.** The 2 rejected
offers were `b2-realme-11proplus-parent-black` and `b3-realme-11proplus-parent-black` — reason
«Название товара дублируется в данном файле». Root cause: **b2 vs b3 are different book cases** (WB
desc: b1/b2/b5 = «**три** кармашка-кардхолдера» = 3 card slots; b3 = «**несколько** кармашков» =
multiple), but the flat `book` recipe gave both the same title for the same phone+colour. Fix: book
title now encodes slot count — b1/b2/b5 → «с 3 отделениями для карт и подставкой», b3 → «с
несколькими отделениями для карт и подставкой» (in both `build_price.py` and `batch_all.py`). Re-push
→ **status=COMPLETED total=155 success=155 notMapped=0 fail=0.** Price-list `<model>` now unique per
SKU. NOTE: the 2 live CARD names (set at moderation) are still the old identical text; to make the
storefront card titles distinct too, delete those 2 in the cabinet and recreate via
`batch_all.py <sku>` (no edit API). General rule: **product names must be unique across the whole
price-list file** — differentiate any same-phone/same-colour cards that share a case type.

---

## 2026-08-03 — real photo source found: Yandex.Disk `BRICASE KZ/ФОТО`

**[live] The "photo refresh" photo source is a Yandex.Disk folder, not (only) WB.** User provided a
Yandex OAuth token (`YANDEX_DISK_TOKEN` in `.env`, `cloud-api.yandex.net` — reachable without extra
network allowlisting, unlike halykmarket.kz/wildberries which need Custom network access). Under
`disk:/BRICASE KZ/` there are business folders `WAREHOUSE` (stock sync source, see
`HM_SYNC_HANDOUT.md` §6), `ФОТО` (photos), `ЦВЕТА ТОВАРОВ`, `ШАБЛОНЫ для СОЗДАНИЯ ТОВАРОВ`, etc.

**`ФОТО` structure:** one subfolder per SKU, named with the **same vendorCode convention** as the
catalogue (`<caseType>-<phonemodel>-parent-<colorToken>`, e.g. `b3-samsung-s24ultra-parent-red` — the
pilot SKU from the 2026-07-30 native-photo plan). Inside, PNG files named `<sku>-r<N>v<M>.png`
("render N, variant M") — **native ~3:4 aspect** (e.g. 1582×2110), custom-branded infographic-style
product renders (title banner + feature-callout text baked into the image), distinct from and higher
production value than the plain WB CDN photos. File count per folder is **not fixed** — sampled
folders had anywhere from 1 to 16 images (multiple render/variant candidates for some SKUs, a single
hero shot for others). **[open] no established rule yet for which file(s) to pick when a folder has
multiple** — needs a decision (most recent r/v? all of them as a gallery? user curates?).

**[live] Coverage vs the 155-SKU catalogue (checked 2026-08-03):** 120 folders present, of which 118
match a real SKU exactly. **37 SKUs have no Yandex folder yet** — heavily concentrated in the iPhone
17 / 17 Pro / 17 Pro Max C7/C10/C5/C6 families (32 of the 37), plus scattered others
(`b2-redminote11-4g-parent-black`, `b3-tecno-povaneo2-parent-black-cs`,
`realme-14proplus-parent-fuchsia-cs`, `xiaomi12pro-parent-black-cs`, `c7-samsung-s24-parent-col4`).
**2 orphan folders don't match any current SKU** (likely stale/renamed): `b3-tecno-povaneo2-parent-black`
(SKU has a `-cs` suffix the folder lacks) and `redminote10-parent-darkred-cs` (no matching SKU at all).

**[open] Plan not yet decided:** whether the 37 uncovered SKUs fall back to the native-WB-photo recipe
(2026-07-30 plan, already in `batch_all.py`) while the 118 covered ones use the Yandex renders, and
how multi-file folders get reduced to a photo set. Needs user confirmation before building the
downloader/recreate pipeline — this swaps live storefront images on ~118+ real product cards.
