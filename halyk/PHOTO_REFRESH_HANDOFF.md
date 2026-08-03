# Halyk Market — phone-case photo refresh: handoff

Standalone summary for continuing this on a **local machine** (or a fresh session) with real
network access to Halyk/WB — no cloud-sandbox network-allowlist dance needed there. Full raw
history lives in `../HALYK_MARKET_API.md` (700+ lines, chronological log) and
`HM_SYNC_HANDOUT.md` (order/stock sync spec); this file is the condensed "what are we doing and
why" for the photo-refresh task specifically.

---

## 1. The business

**Bricase KZ**, БИН/ИИН `000117600035`. Sells phone cases. Catalogue mirrors a Wildberries KZ
(mag1) supplier account onto the Halyk Market (Kazakhstan) marketplace via Halyk's merchant API.

**155 SKUs, all live on Halyk**, by case type (vendorCode prefix):
- `c7` 37, `c10` 21, `c6` 6, `c5` 4, `c2` 1 — "C-series" hard cases
- `b1`/`b2`/`b3`/`b5` = 22 — book-leather cases
- phone-brand-named (`samsung/google/honor/huawei/...`) = 64 — soft-touch cases

SKU convention: `<caseType>-<phonemodel>-parent-<colorToken>`, e.g.
`c7-iphone-17promax-parent-col8`. Colour families were merged into single storefront
colour-selector products via a cabinet-only Excel upload (`build_merge.py` →
"Соединение вариаций товаров") — 155 cards → **82 storefront products** (37 merged families + 45
standalone).

**1 live customer order** as of 2026-07-30: `0013597323-1`, SKU
`c7-samsung-s23ultra-parent-col7`. **Standing rule: re-verify orders/stock live before any bulk
action — never trust a cached note** (`GET /gw/merchant/public/order/v2`). Exclude any SKU with a
live order from delete/recreate.

---

## 2. Credentials & access

All in `../.env` (gitignored, dies with a fresh cloud container — recreate from `.env.example`
plus the values below; on a local machine just keep the `.env` file):

```
HALYK_CLIENT_ID=HMM_000117600035
HALYK_CLIENT_SECRET=<from Halyk password-reset email, api-noreply@halykmarket.com>
HALYK_ENV=prod
WB_KZ_TOKEN=<WB KZ supplier token, expires 2026-12-21>
YANDEX_DISK_TOKEN=<Yandex OAuth token for the BRICASE KZ Disk account>
```

- Halyk auth: `POST https://halykmarket.kz/gw/auth/token`, **JSON body** (form-encoded → 500 not
  401), `{"grant_type":"client_credentials","client_id":...,"client_secret":...}` →
  `access_token` (~2h). **Rate-limits (429) if minted per call** — cache & reuse.
- Two Halyk hosts: `halykmarket.kz/gw` (token, orders, **card create, photo upload**) and
  `api.halykmarket.com/api/merchant/v1` (order state changes, **price/stock upload**).
- WB: `content-api.wildberries.ru` (card data), `discounts-prices-api.wildberries.ru` (pricing).
  Header `Authorization: <token>`, no `Bearer` prefix.
- Yandex.Disk: `cloud-api.yandex.net`, header `Authorization: OAuth <token>`.
- **In a cloud sandbox only:** these hosts need the environment's network policy set to *Custom*
  with them allowlisted, or every call 403s at the proxy (not the server). Not an issue on a
  normal local machine with open internet.

---

## 3. Photo-refresh backstory (why we're redoing photos at all)

1. Cards were originally created with photos **square-padded to 1200×1200 white background**,
   following Halyk's stated photo spec (1:1, white bg, min 500×500). Moderation accepted this —
   turned out **photos were never the actual rejection blocker** (missing characteristics were).
2. **2026-07-30 correction:** Halyk actually displays case cards **portrait 3:4** in the cabinet,
   and WB's native images already are 900×1200 (3:4), with `photos[0]` being a colourful
   marketing "cover" frame. So the square/white-pad step was unnecessary work — `batch_all.py`
   was changed to upload **native WB images in WB order** (cover-first, no reshaping). This is
   the state the branch was in before this session. **No photo-edit API exists** — the only way
   to change a live card's photos is delete (cabinet-only for approved cards) + recreate via API
   with the same `merchantProductCode`.
3. **2026-08-03 (this session):** the user supplied a Yandex.Disk OAuth token. Investigating it
   found the *real* intended photo source — see §4. This supersedes plain WB photos as the
   primary source where available.

---

## 4. Photo source: Yandex.Disk `BRICASE KZ/ФОТО`

Under the user's Yandex.Disk account, folder `disk:/BRICASE KZ/` has: `WAREHOUSE` (stock-sync
source, see `HM_SYNC_HANDOUT.md` §6), **`ФОТО`** (photos — this task), `ЦВЕТА ТОВАРОВ`, `ШАБЛОНЫ
для СОЗДАНИЯ ТОВАРОВ`, and others (unrelated — this is the user's general personal Disk, the
token is not scoped to just this one folder — be careful not to touch/list anything outside
`BRICASE KZ/`).

**`ФОТО` structure:** one subfolder per SKU, **same vendorCode naming as the catalogue**
(confirmed e.g. `b3-samsung-s24ultra-parent-red` — the pilot SKU from the 2026-07-30 plan).
Inside: PNG files named `<sku>-r<N>v<M>.png` ("render N, variant M") — native ~3:4
(e.g. 1582×2110), **custom branded infographic-style renders** (title banner + feature-callout
text baked in), clearly higher production value than plain WB photos. Verified by downloading and
viewing the pilot SKU's image — a proper finished product photo, not a placeholder.

**File count per folder varies, not fixed:** sampled folders had 1, 2, 11, or 16 files. Some SKUs
have a single hero shot; others have many candidate render/variant combinations.

**Coverage checked 2026-08-03** (script: list `wb_cards.json` vendorCodes vs. Yandex folder
names):
- **120 folders present, 118 match a real SKU exactly.**
- **37 SKUs have no Yandex folder yet** — heavily concentrated in the **iPhone 17 / 17 Pro / 17
  Pro Max** C7/C10/C5/C6 families (32 of the 37), plus scattered others:
  `b2-redminote11-4g-parent-black`, `b3-tecno-povaneo2-parent-black-cs`,
  `realme-14proplus-parent-fuchsia-cs`, `xiaomi12pro-parent-black-cs`, `c7-samsung-s24-parent-col4`.
- **2 orphan folders don't match any current SKU** (likely stale/typo'd): `b3-tecno-povaneo2-parent-black`
  (real SKU has a `-cs` suffix the folder lacks) and `redminote10-parent-darkred-cs` (no matching
  SKU at all — check if this is meant to be `redminote10pro-parent-darkred-cs` or similar).

---

## 5. Open decisions (need a human call before automating)

1. **The 37 uncovered SKUs** — fall back to native-WB-photo recipe (already coded), skip them
   until their Yandex folder shows up, or hold the *entire* refresh until all 155 are covered?
2. **Multi-render folders** — when a SKU folder has several files, use all as a gallery (WB-style
   multi-photo card), pick only the newest `r`-group, or have the user point at the chosen file(s)
   per SKU (e.g. via a naming convention or a marker file)?
3. **The 2 orphan folder names** — fix by renaming on Disk, or by aliasing in the pipeline?

---

## 6. The algorithm (once decisions above are made + credentials/network are live)

Halyk has **no card-edit API** and **cannot delete an approved card via API** (`DELETE
/draft/product/<id>` 404s on approved cards, confirmed live). So refreshing a live card's photos
is inherently a delete(cabinet)+recreate(API) cycle:

1. **Re-verify live orders** (`GET /gw/merchant/public/order/v2`, no cached assumptions). Build
   the exclude-list of any SKU with an active order (as of 2026-07-30: just
   `c7-samsung-s23ultra-parent-col7`, but re-check).
2. **Pilot first:** confirm the recreate recipe end-to-end on one already-tested SKU
   (`b3-samsung-s24ultra-parent-red` was the designated pilot) before touching the rest. User
   previously indicated this pilot succeeded manually in the cabinet — a fresh session should
   re-verify the live card, not assume.
3. **Per SKU** (for all ~153 no-order SKUs, batched by however many the user is willing to
   manually process at once — the cabinet-delete step does not have a bulk API):
   a. **Manual step (cabinet, user or someone with cabinet login):** delete the approved card in
      the Halyk Partners cabinet. This frees the `merchantProductCode` for reuse.
   b. **Fetch photo(s):** from `BRICASE KZ/ФОТО/<sku>/` (Yandex.Disk API,
      `GET /v1/disk/resources?path=disk:/BRICASE KZ/ФОТО/<sku>`, download via the returned `file`
      URL) if the folder exists; else fall back per the §5 decision.
   c. **Recreate via API:** `halyk/batch_all.py <sku>` already has the full attribute/price/stock
      recipe (all 14 category-20004 characteristics, ENUM values as numeric IDs, two-field price,
      loanPeriod) — only the photo-sourcing step (currently pulling from
      `c["photos"][*]["big"]` on WB) needs to be extended to prefer the Yandex render(s) when
      present. Submits `POST /gw/merchant/public/draft/product/moderation` → 202 + draft id.
   d. **Poll** `GET /gw/merchant/public/draft/product/<id>` until `productDraftResponse.status`
      is `SUCCESS`/`REJECT` (note: status is nested there, not top-level `productDraftStatus` —
      a earlier-doc naming trap).
4. **Rebuild + push price/stock:** `halyk/build_price.py` then `POST
   api.halykmarket.com/api/merchant/v1/offers/upload` (multipart XML) — price/stock is a
   *separate* step from card creation; recreated cards start with none until this runs. Must be a
   **FULL** upload (every SKU, every time) or omitted offers can deactivate.
5. **Re-merge colour families:** recreated cards get new draft ids and lose any prior grouping.
   Re-run `halyk/build_merge.py` to rebuild `merge_filled.xlsx`, then **manually re-upload it in
   the Halyk cabinet** (Товары → Объединение товаров → Соединение вариаций товаров — this step has
   no API, cabinet-login only, separate auth from the merchant API).
6. **Spot-check the storefront** (halykmarket.kz) for a few recreated families to confirm photos
   look right and colour selectors still work.

---

## 7. Known gotchas (don't rediscover these)

- Token 429s if minted per call — cache and reuse (~2h TTL).
- ENUM attributes (Тип 10070, Материал 10078, Совместимость 10081) need the **numeric
  `classAttrValueId`**, not the name — names silently don't register.
- **ALL 14 category-20004 characteristics must be filled** (only 3 are marked `required` by the
  API, but moderation rejects at <100% completeness regardless).
- `loanPeriod` in the price-list XML **must be ≥3** (a real installment term) — `0` silently fails
  that offer.
- `storeId="Bricase KZ_pp1"` **with the space**, not an underscore.
- A **rejected** draft is stuck exactly like an approved one — cabinet-only to clear, then API can
  recreate with the same code.
- Don't enumerate order/entry ids on the `api.halykmarket.com` relationship endpoints — a
  placeholder id returned real (not-ours) data once; only ever follow ids from your own order
  list.
- Product names must be unique across the *entire* price-list file, not just per SKU pair —
  same-phone/same-colour cards sharing a case type need visibly different titles.
- Stock must be refreshed **≥ every 90 days** or a card auto-archives.

---

## 8. Files

```
HALYK_MARKET_API.md          full chronological log (source of truth for anything not covered above)
halyk/
  PHOTO_REFRESH_HANDOFF.md   this file
  HM_SYNC_HANDOUT.md         order intake + stock/price push spec (separate from photo refresh)
  README.md                  script usage
  batch_all.py               card creator (needs: extend photo step for Yandex source)
  build_price.py             rebuilds price_all.xml from WB price/stock
  build_merge.py             rebuilds merge_filled.xlsx for cabinet colour-grouping upload
  finalize.py                historical one-off poller from the 2026-07-29/30 catalogue build
  data/                      compat_opts.json, color_opts.json, wb_cards.json, stock.json (committed)
  out/                       generated run artifacts (gitignored)
halyk_market/                Python client for the merchant API (token, orders, CLI) — order side, not the ad-hoc catalogue scripts
```
