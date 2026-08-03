# Halyk Market Migration — Status & Next Steps
_Last live-verified: 2026-08-03. Full technical log: `HALYK_MARKET_API.md`. Order/stock-sync spec for another builder: `halyk/HM_SYNC_HANDOUT.md`._

## What this project is
Migrating the Wildberries KZ (WB) phone-case catalogue for seller **Bricase KZ**
(БИН 000117600035) onto **Halyk Market** via its merchant API, then automating
price/stock sync back to the warehouse.

Repo: `van-stepan/cian_project`, branch **`claude/mobile-market-api-hztllb`**.
Toolchain + data snapshot live in `halyk/` (scripts) and `halyk/data/` (WB card
export, stock snapshot, Halyk enum maps). Credentials are runtime-only in a
gitignored `.env` — never committed, never printed.

---

## Where things stand (verified live, not from a cached note)

| Item | Status |
|---|---|
| Cards created | **155 / 155** WB SKUs live on Halyk (7 case types) |
| Priced & mapped | **155 / 155** (price-list upload: `success=155, notMapped=0, fail=0`) |
| Colour-variation merge | **37 / 37 families merged**, 0 errors → storefront is 82 products |
| Live orders | **1** — `0013597323-1`, SKU `c7-samsung-s23ultra-parent-col7`, status `DELIVERY_PVZ` |
| Photo-pipeline upgrade | **1 pilot card recreated & approved** (`b3-samsung-s24ultra-parent-red`, draft id 641697, `SUCCESS`) with native WB 3:4 photos; **153 more cards queued**, blocked on Yandex.Disk network access (see below) |

## ⚠️ Standing rule — do not skip
**Always re-check orders and live stock/status against the Halyk API live before answering.**
A cached note said "0 orders" once and was wrong — there was 1 real order. Never trust a
memory-file note for anything time-sensitive; always re-query.

---

## Key API facts (condensed — full detail in `HALYK_MARKET_API.md`)

- **Two hosts**: `halykmarket.kz/gw` (token, cards, photo upload, order list/detail) and
  `api.halykmarket.com/api/merchant/v1` (order status changes, price-list upload).
- **Auth**: `POST /gw/auth/token`, **JSON body** (form-encoded → HTTP 500, not 401). Token ~2h,
  cache it (429 if re-minted per call).
- **Card creation**: `POST /gw/merchant/public/draft/product/moderation` → 202 `{id}` → poll
  `GET /gw/merchant/public/draft/product/<id>` → real status is at
  `productDraftResponse.status` (`CHECK→MODERATION→SUCCESS/REJECT`), rejection reason in
  top-level `comment`.
- **No card-edit API.** Changing a live card (title, photos, attrs) requires: delete in the
  **cabinet only** (no delete endpoint) → recreate via API with a fresh payload. The
  `merchantProductCode` (=vendorCode) is reusable once the cabinet delete frees it.
- **Price/stock**: `POST api.halykmarket.com/api/merchant/v1/offers/upload` (multipart XML) →
  `{id}` → poll `.../offers/upload/status/<id>`. Status flow is
  **`CREATED → PROCESSING → COMPLETED|UPLOADED_WITH_ERRORS|FAILED`** — CREATED and PROCESSING
  are BOTH non-terminal, a common polling bug. `loanPeriod` must be ≥3 (0 → silent fail). Must be
  a FULL file (every SKU every time). **All `<model>` names in the file must be globally
  unique** — two identical names anywhere in the file get rejected as duplicates (this bit us:
  two different book-case variants for the same phone+colour had identical auto-generated
  titles; fixed by encoding the distinguishing feature — card-slot count — into the title).
- **Colour-variation merge**: NOT part of the merchant API at all (confirmed: every plausible
  endpoint returns Spring "No static resource" / 404). It's a **cabinet-only** feature —
  Товары → Добавление товара → Объединение товаров → Вариации товара → upload an Excel template
  (`sku | name | Код вариации | Цвет`; same Код вариации ⇒ merged into one product with Цвет as
  the selector). Template + builder: `halyk/build_merge.py` → `merge_filled.xlsx`. Must be
  uploaded by a human in the cabinet (separate bank-grade login from our API token).
- **Compatibility catalogue gap**: Halyk's «Совместимость» dropdown has 231 phone models but is
  missing ~22 of ours entirely (Google Pixel, OnePlus, several Realme/Tecno/Xiaomi/Samsung
  models) — no API to add custom values. Field is optional; blank passes moderation fine. A
  Russian request to Halyk/Qoldau asking them to add these models was drafted (in chat, not yet
  sent) — send it, then re-tag the ~46 affected cards once they confirm.
- **Photos**: Halyk displays case photos **portrait 3:4**, not square — an earlier assumption
  that square/white-bg was required was overcautious and unnecessary. Native WB images (900×1200,
  3:4) are the right format; `photos[0]` from WB is the colourful marketing cover and should be
  the Halyk card cover too.
- **Transient Halyk infra flaps observed** (photo-upload minio DNS 409, offers-upload 500) —
  server-side, resolved on their end; just retry with backoff, don't treat as our bug.

---

## Immediate next step (blocked — needs you)

**Goal**: recreate the other 153 no-order cards with the new WB-native 3:4 photo pipeline (per
your standard photo sets), using:
- Photo folder: `Yandex.Disk: ВНЕШНИЕ ЗАДАНИЯ - Алмаз (NEW)/! ОБЩАЯ ПАПКА СО ВСЕМИ ФОТО`
- Mapping file: `Yandex.Disk: ОБЩАЯ ПАПКА/STD_PHOTO_SETS.xlsx`

**Blocker**: Yandex.Disk API access (`cloud-api.yandex.net`, `downloader.disk.yandex.ru`) needs
to be in this session's network allowlist. The environment's Custom network policy was updated
with these domains, but **network policy is fixed per-session at start time — it does not
hot-reload into an already-running session.** A brand-new session (same environment/repo, `+` on
the sessions screen) is required to pick up the change.

**When resuming in a new session**, tell it to:
1. Check out branch `claude/mobile-market-api-hztllb` in `van-stepan/cian_project` (NOT master —
   master has no trace of this work; everything is on this branch).
2. Read `HALYK_MARKET_API.md` and this file for context.
3. Re-provide the Yandex OAuth token (env value, does not persist across sessions) — or generate
   a fresh one via https://oauth.yandex.ru/client/new (see chat history for the exact steps: web
   service app, redirect URI `https://oauth.yandex.ru/verification_code`, "Чтение всего Диска"
   scope, then visit the authorize URL to get the token on-screen).
4. Pull `STD_PHOTO_SETS.xlsx` + the photo folder, map photo sets to the 7 case types, then for
   each of the 153 no-order SKUs: **you delete the old card in the cabinet** (no delete API) →
   script recreates it with the matching photo set (native 3:4, cover-first) → re-push the full
   price-list → re-run the colour-merge upload (`build_merge.py` → cabinet).
5. **Exclude `c7-samsung-s23ultra-parent-col7` from any delete/recreate** — it has the one live
   order. Always re-verify the live order list first in case a new order has come in since.

## Other open items (lower priority, not blocking)
- Send the Qoldau/Halyk-support request for the ~22 missing compatibility models (drafted, not
  yet sent) — Russian text is in chat history, can be regenerated on request.
- Build the actual warehouse → Halyk stock-sync automation (order arrives → decrement warehouse
  qty → rebuild price-list → upload). Spec for this is in `halyk/HM_SYNC_HANDOUT.md`.
- 45 single-colour models were never merge-eligible (correctly left standalone) — no action needed.

## Files to know
- `HALYK_MARKET_API.md` — full chronological discovery log (long, but authoritative for any
  "why does X work this way" question).
- `halyk/batch_all.py` — card creator (modes: `creminder`, `tests`, `softtouch`, `book`, or a
  single SKU). Photo step now uses native WB 3:4 images.
- `halyk/build_price.py` — builds the full 155-offer price-list XML from WB data + Halyk's
  attribute catalogue.
- `halyk/build_merge.py` — builds the colour-merge Excel template from the 155 cards.
- `halyk/data/` — `wb_cards.json` (WB export), `stock.json` (FBS stock snapshot — irreplaceable,
  came from user's warehouse export), `compat_opts.json`/`color_opts.json` (Halyk enum dumps).
- `halyk/HM_SYNC_HANDOUT.md` — standalone spec for order-intake + stock-sync, written for a
  different builder/session to consume without this conversation's context.
