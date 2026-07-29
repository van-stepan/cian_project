# Halyk Market catalogue pipeline

Toolchain that mirrors the Wildberries KZ catalogue onto Halyk Market via the merchant API.
Full API notes live in `../HALYK_MARKET_API.md`. Credentials are read at runtime from
`../.env` (gitignored — never committed): `HALYK_CLIENT_ID`, `HALYK_CLIENT_SECRET`, `WB_KZ_TOKEN`.
A freshly-reclaimed container has no `.env`; recreate it before running.

## Scripts
- `batch_all.py <mode>` — idempotent card creator for every case type.
  Modes: `creminder` (C10/C5/C6/C2 remainders), `tests` (3 new-type probes),
  `softtouch` (64), `book` (22), or a single vendorCode. `already_exists` → ALREADY.
  Env `SOFTTOUCH_UNIVERSAL=1` marks catalogue-missing models as compat "Универсальный".
- `build_price.py` — rebuilds a FULL 155-offer price-list (`price_all.xml`), mapping by
  SKU; price = WB discountedPrice, stock = WB-остаток, loanPeriod=3.
- `finalize.py` — polls the 3 new-type test drafts; on SUCCESS auto-runs `book`+`softtouch`
  (with the Универсальный fallback only if the no-compat probe alone rejects), then rebuilds
  and re-pushes the price-list. Writes `FINAL_STATUS.json`.

## Data (`data/`)
- `wb_cards.json` — 155 WB cards (regenerable from WB Content API).
- `stock.json` — FBS stock snapshot (col idx 12 = WB остаток). **Not API-regenerable** — sourced
  from the user's warehouse export; kept here as the durable copy.
- `compat_opts.json` / `color_opts.json` — Halyk category-20004 enum maps (regenerable from the form).

Scripts default their working dir to the session scratchpad; point them at this folder by
copying `data/*` alongside the scripts (or set the `SP` path) when running from a fresh clone.
