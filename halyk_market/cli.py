# -*- coding: utf-8 -*-
"""Command line entry point for the Halyk Market merchant API.

Read-only:
    python -m halyk_market.cli config
    python -m halyk_market.cli token
    python -m halyk_market.cli orders --status APPROVED_BY_BANK --size 20
    python -m halyk_market.cli new
    python -m halyk_market.cli order 0008449018-1
    python -m halyk_market.cli entries 11111111
    python -m halyk_market.cli raw GET /merchant/public/order/v2 --param size=5

State changing (each needs --yes, since these act on real customer orders):
    python -m halyk_market.cli accept 11111111 1111111111-1 --yes
    python -m halyk_market.cli courier 11111111 1111111111-1 --yes
    python -m halyk_market.cli send-otp 11111111 1111111111-1 --yes
    python -m halyk_market.cli complete 11111111 1111111111-1 4007 --yes
    python -m halyk_market.cli cancel 11111111 1111111111-1 MERCHANT_OUT_OF_STOCK --yes
"""

import argparse
import json
import logging
import sys

from .client import (
    CancellationReason,
    HalykMarketClient,
    HalykMarketError,
    OrderStatus,
)
from .config import Config


STATUSES = [v for k, v in vars(OrderStatus).items() if not k.startswith("_")]
REASONS = [v for k, v in vars(CancellationReason).items() if not k.startswith("_")]


def _dump(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _parse_pairs(pairs):
    parsed = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise argparse.ArgumentTypeError("expected KEY=VALUE, got %r" % pair)
        key, value = pair.split("=", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def build_parser():
    parser = argparse.ArgumentParser(prog="halyk_market", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env", dest="environment", choices=["prod", "test"], default=None,
                        help="Halyk Market environment (default: HALYK_ENV or prod)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Log every HTTP call")
    parser.add_argument("--no-token-cache", dest="no_token_cache", action="store_true",
                        help="Do not reuse or write the on-disk token cache")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("config", help="Show the resolved configuration with the secret masked")
    sub.add_parser("token", help="Print an access token, reusing the cache when valid")
    sub.add_parser("logout", help="Delete the cached access token")

    orders = sub.add_parser("orders", help="List orders")
    orders.add_argument("--status", choices=STATUSES)
    orders.add_argument("--page", type=int, default=1)
    orders.add_argument("--size", type=int, default=20, help="Up to 100")
    orders.add_argument("--order-number", dest="order_number")
    orders.add_argument("--start-date", dest="start_date", metavar="YYYY-MM-DD")
    orders.add_argument("--end-date", dest="end_date", metavar="YYYY-MM-DD")

    new = sub.add_parser("new", help="List orders awaiting acceptance (APPROVED_BY_BANK)")
    new.add_argument("--page", type=int, default=1)
    new.add_argument("--size", type=int, default=20)

    order = sub.add_parser("order", help="Order detail by order number (waybill, OTP, courier)")
    order.add_argument("order_number")

    entries = sub.add_parser("entries", help="Line items of an order, by internal order id")
    entries.add_argument("order_id")

    product = sub.add_parser("product", help="Product behind an order line, by entry id")
    product.add_argument("entry_id")

    pos = sub.add_parser("pickup-point", help="Pickup point of an order line, by entry id")
    pos.add_argument("entry_id")

    products = sub.add_parser("products", help="Product details for one or more order ids")
    products.add_argument("order_ids", nargs="+")

    accept = sub.add_parser("accept", help="Accept a new order")
    accept.add_argument("order_id")
    accept.add_argument("code")
    accept.add_argument("--count-place", dest="count_place", type=int)
    accept.add_argument("--pos-code", dest="pos_code")

    courier = sub.add_parser("courier", help="Request a Halyk Market courier")
    courier.add_argument("order_id")
    courier.add_argument("code")

    send_otp = sub.add_parser("send-otp", help="Send the handover OTP to the customer")
    send_otp.add_argument("order_id")
    send_otp.add_argument("code")

    complete = sub.add_parser("complete", help="Complete an order with the customer's OTP")
    complete.add_argument("order_id")
    complete.add_argument("code")
    complete.add_argument("security_code")

    cancel = sub.add_parser("cancel", help="Cancel an order not yet handed to delivery")
    cancel.add_argument("order_id")
    cancel.add_argument("code")
    cancel.add_argument("reason", choices=REASONS)

    for mutating in (accept, courier, send_otp, complete, cancel):
        mutating.add_argument("--yes", action="store_true",
                              help="Required: confirms this changes a real order")

    raw = sub.add_parser("raw", help="Call an arbitrary authenticated endpoint")
    raw.add_argument("method", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    raw.add_argument("path")
    raw.add_argument("--base", choices=["gw", "api"], default="gw",
                     help="Which host to resolve a relative path against (default: gw)")
    raw.add_argument("--param", dest="params", action="append", metavar="KEY=VALUE")
    raw.add_argument("--header", dest="headers", action="append", metavar="NAME=VALUE")
    raw.add_argument("--body", help="JSON request body")

    return parser


MUTATING = {"accept", "courier", "send-otp", "complete", "cancel"}


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 2

    if args.command in MUTATING and not args.yes:
        print("%s changes a real customer order. Re-run with --yes to confirm." % args.command,
              file=sys.stderr)
        return 2

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    config = Config.from_env(environment=args.environment)

    if args.command == "config":
        _dump(config.masked())
        return 0

    try:
        client = HalykMarketClient(config=config, use_token_cache=not args.no_token_cache)

        if args.command == "logout":
            removed = client.clear_token_cache()
            print("Cleared %s" % client.token_cache_path if removed else "No cached token.")

        elif args.command == "token":
            _dump({"access_token": client.authenticate()})

        elif args.command == "orders":
            _dump(client.get_orders(status=args.status, page=args.page, size=args.size,
                                    order_number=args.order_number,
                                    start_date=args.start_date, end_date=args.end_date))

        elif args.command == "new":
            _dump(client.get_new_orders(page=args.page, size=args.size))

        elif args.command == "order":
            _dump(client.get_order(args.order_number))

        elif args.command == "entries":
            _dump(client.get_order_entries(args.order_id))

        elif args.command == "product":
            _dump(client.get_entry_product(args.entry_id))

        elif args.command == "pickup-point":
            _dump(client.get_entry_point_of_service(args.entry_id))

        elif args.command == "products":
            _dump(client.get_products_by_order(args.order_ids))

        elif args.command == "accept":
            _dump(client.accept_order(args.order_id, args.code,
                                      count_place=args.count_place, pos_code=args.pos_code))

        elif args.command == "courier":
            _dump(client.request_courier(args.order_id, args.code))

        elif args.command == "send-otp":
            _dump(client.send_customer_otp(args.order_id, args.code))

        elif args.command == "complete":
            _dump(client.complete_order(args.order_id, args.code, args.security_code))

        elif args.command == "cancel":
            _dump(client.cancel_order(args.order_id, args.code, args.reason))

        elif args.command == "raw":
            base = config.gw_base if args.base == "gw" else config.api_base
            _dump(client.request(args.method, args.path, base=base,
                                 params=_parse_pairs(args.params),
                                 extra_headers=_parse_pairs(args.headers),
                                 json_body=json.loads(args.body) if args.body else None))

    except ValueError as exc:
        print("Configuration error: %s" % exc, file=sys.stderr)
        return 2
    except HalykMarketError as exc:
        print("API error: %s" % exc, file=sys.stderr)
        if exc.payload is not None:
            print(json.dumps(exc.payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
