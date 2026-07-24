# -*- coding: utf-8 -*-
"""Диагностика WB-токена: печатает срок/область действия токена (из JWT) и
статусы обращения к разным API WB. Помогает понять, каких категорий не хватает
(например «Статистика»), не истёк ли токен и не «песочница» ли это.

Запуск (из папки wb_export, рядом с wb_udmurtia_export.py):
    python wb_ping.py --config "C:\\...\\CONFIG.py" ^
        --config-key credentials.RU.mag1.wb.headers.Authorization

Сам токен и подпись JWT не печатаются — вывод безопасно прислать.
"""
import argparse
import base64
import json

import requests

from wb_udmurtia_export import load_token_from_config

# (метод, url) — набор проверок доступа по разным категориям.
CHECKS = [
    ("GET", "https://common-api.wildberries.ru/ping"),
    ("GET", "https://common-api.wildberries.ru/api/v1/seller-info"),
    ("GET", "https://statistics-api.wildberries.ru/ping"),
    ("GET", "https://statistics-api.wildberries.ru/api/v1/supplier/incomes"
            "?dateFrom=2024-01-01"),
    ("GET", "https://seller-analytics-api.wildberries.ru/ping"),
    ("GET", "https://documents-api.wildberries.ru/api/v1/documents/categories"
            "?locale=ru"),
]


def decode_jwt_claims(token: str):
    """Достаёт полезную нагрузку JWT (без подписи) и оставляет только
    несекретные поля области/срока действия."""
    try:
        raw = token.strip()
        if raw.lower().startswith("bearer "):
            raw = raw[7:].strip()
        parts = raw.split(".")
        if len(parts) < 2:
            return "(не похоже на JWT)"
        seg = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(seg.encode()))
        interesting = ("s", "sid", "exp", "iat", "t", "ent", "sandbox", "oid")
        return {k: payload.get(k) for k in interesting if k in payload}
    except Exception as e:  # noqa: BLE001
        return f"(не удалось декодировать: {e})"


def main() -> None:
    ap = argparse.ArgumentParser(description="Диагностика доступа WB-токена.")
    ap.add_argument("--config", required=True, help="Путь к CONFIG.py.")
    ap.add_argument("--config-key",
                    default="credentials.RU.mag1.wb.headers.Authorization",
                    help="Путь к токену в CONFIG.py через точку.")
    args = ap.parse_args()

    token = load_token_from_config(args.config, args.config_key.split("."))
    starts_bearer = token.lower().startswith("bearer ")
    print(f"Токен получен. Длина: {len(token)}. С префиксом 'Bearer ': "
          f"{starts_bearer}")
    print(f"JWT-поля: {decode_jwt_claims(token)}")
    print("  подсказка: 's' — маска категорий; 'exp' — срок (unix); "
          "'sandbox'/'t' — тестовый токен.\n")

    session = requests.Session()
    session.headers.update({"Authorization": token, "Accept": "application/json"})
    for method, url in CHECKS:
        try:
            r = session.request(method, url, timeout=30)
            snippet = " ".join(r.text[:200].split())
            print(f"{r.status_code}  {url}")
            print(f"      {snippet}")
        except Exception as e:  # noqa: BLE001
            print(f"ERR  {url}\n      {e}")


if __name__ == "__main__":
    main()
