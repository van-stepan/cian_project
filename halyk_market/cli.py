# -*- coding: utf-8 -*-
"""Command line entry point for the Halyk Market merchant API.

    python -m halyk_market.cli config
    python -m halyk_market.cli token
    python -m halyk_market.cli orders --filter code=1234567
    python -m halyk_market.cli order 1234567
    python -m halyk_market.cli raw GET /api/merchant/v1/orders
"""

import argparse
import json
import logging
import sys

from .client import HalykMarketClient, HalykMarketError
from .config import Config


def _dump(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _parse_filters(pairs):
    filters = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise argparse.ArgumentTypeError("--filter expects field=value, got %r" % pair)
        field, value = pair.split("=", 1)
        filters[field.strip()] = value.strip()
    return filters


def build_parser():
    parser = argparse.ArgumentParser(prog="halyk_market", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env", dest="environment", choices=["prod", "test"], default=None,
                        help="Which Halyk Market environment to talk to (default: HALYK_ENV or prod)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Log every HTTP call")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("config", help="Show the resolved configuration with the secret masked")
    sub.add_parser("token", help="Request an access token and print it")

    orders = sub.add_parser("orders", help="List orders")
    orders.add_argument("--filter", dest="filters", action="append", metavar="FIELD=VALUE",
                        help="Repeatable order filter, e.g. --filter code=1234567")
    orders.add_argument("--page", type=int)
    orders.add_argument("--per-page", type=int, dest="per_page")

    order = sub.add_parser("order", help="Fetch one order by its code")
    order.add_argument("code")

    raw = sub.add_parser("raw", help="Call an arbitrary authenticated endpoint")
    raw.add_argument("method", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    raw.add_argument("path")
    raw.add_argument("--param", dest="params", action="append", metavar="KEY=VALUE")
    raw.add_argument("--body", help="JSON request body")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
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
        client = HalykMarketClient(config=config)

        if args.command == "token":
            _dump({"access_token": client.authenticate()})

        elif args.command == "orders":
            _dump(client.get_orders(filters=_parse_filters(args.filters),
                                    page=args.page, per_page=args.per_page))

        elif args.command == "order":
            _dump(client.get_order_by_code(args.code))

        elif args.command == "raw":
            params = _parse_filters(args.params)
            body = json.loads(args.body) if args.body else None
            _dump(client.request(args.method, args.path, params=params, json_body=body))

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
