# -*- coding: utf-8 -*-
"""
Выгрузка поставок и приёмок по складам Wildberries в Удмуртии (склад «Ижевск»).

Скрипт ходит в официальные API Wildberries под вашим API-ключом и собирает:
  1. Поступления/поставки на склад (incomes) — дата, склад, артикул, баркод,
     nmId, количество, дата приёмки. Это и есть подтверждение того, что товар
     был поставлен и принят на складе ВБ в Удмуртии.
  2. Отчёт о платной приёмке (acceptance-report / «акты о приёмке»), привязанный
     к поставкам в Удмуртию по incomeId.

Результат — файл Excel (несколько листов) + CSV-копии.

Данные берутся ТОЛЬКО из вашего собственного кабинета продавца по вашему ключу.
Ничего не выдумывается: если API вернёт пусто — в отчёте будет пусто.

Использование:
    export WB_API_TOKEN="ваш_токен_из_ЛК"      # Настройки -> Доступ к API
    python3 wb_udmurtia_export.py --date-from 2023-01-01 --date-to 2024-12-31

Токен должен иметь доступ к категориям «Статистика» и «Аналитика».
"""

import argparse
import csv
import datetime as dt
import os
import sys
import time
from typing import Any, Dict, Iterable, List, Optional

import requests

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter
    HAVE_OPENPYXL = True
except ImportError:  # Excel-вывод опционален; CSV пишется всегда.
    HAVE_OPENPYXL = False


# --- Эндпоинты официального API Wildberries ---------------------------------
STATISTICS_BASE = "https://statistics-api.wildberries.ru"
ANALYTICS_BASE = "https://seller-analytics-api.wildberries.ru"

INCOMES_PATH = "/api/v1/supplier/incomes"                    # поступления на склад
ACCEPTANCE_PATH = "/api/v1/analytics/acceptance-report"      # платная приёмка

# Ключевые слова для отбора складов Удмуртии. WB-склад в республике — «Ижевск».
# Сравнение регистронезависимое, по вхождению подстроки.
DEFAULT_WAREHOUSE_KEYWORDS = ["ижевск", "izhevsk", "удмурт"]

# Ограничение окна для отчёта приёмки (API принимает интервалы <= 31 дня).
ACCEPTANCE_WINDOW_DAYS = 31


class WBClient:
    """Тонкая обёртка над HTTP с ретраями и обработкой лимитов запросов."""

    def __init__(self, token: str, timeout: int = 60):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": token,
            "Accept": "application/json",
        })
        self.timeout = timeout

    def get(self, base: str, path: str, params: Dict[str, Any],
            max_retries: int = 6) -> Any:
        url = base + path
        delay = 5
        for attempt in range(1, max_retries + 1):
            resp = self.session.get(url, params=params, timeout=self.timeout)

            if resp.status_code == 200:
                return resp.json()

            # 429 — превышен лимит запросов (у статистики WB он строгий:
            # часто не чаще 1 запроса в минуту). Ждём и повторяем.
            if resp.status_code == 429:
                wait = delay * attempt
                print(f"    429 (лимит запросов). Пауза {wait}s и повтор "
                      f"[{attempt}/{max_retries}]...", file=sys.stderr)
                time.sleep(wait)
                continue

            if resp.status_code in (500, 502, 503, 504):
                wait = delay * attempt
                print(f"    {resp.status_code} (ошибка сервера WB). Пауза "
                      f"{wait}s и повтор [{attempt}/{max_retries}]...",
                      file=sys.stderr)
                time.sleep(wait)
                continue

            if resp.status_code in (401, 403):
                raise SystemExit(
                    f"Ошибка авторизации ({resp.status_code}). Проверьте "
                    f"WB_API_TOKEN и что у ключа есть доступ к нужной категории.\n"
                    f"Ответ: {resp.text[:400]}")

            raise SystemExit(
                f"Неожиданный ответ {resp.status_code} от {url}\n"
                f"{resp.text[:400]}")

        raise SystemExit(f"Не удалось получить данные с {url} после "
                         f"{max_retries} попыток.")


def matches_warehouse(name: Optional[str], keywords: Iterable[str]) -> bool:
    if not name:
        return False
    low = name.lower()
    return any(kw in low for kw in keywords)


def fetch_incomes(client: WBClient, date_from: str,
                  keywords: List[str]) -> List[Dict[str, Any]]:
    """Поступления на склады с date_from. Возвращаем только склады Удмуртии."""
    print(f"[1/2] Запрашиваю поступления на склад с {date_from} ...")
    data = client.get(STATISTICS_BASE, INCOMES_PATH, {"dateFrom": date_from})
    if not isinstance(data, list):
        raise SystemExit(f"Неожиданный формат ответа incomes: {type(data)}")

    total = len(data)
    filtered = [row for row in data
                if matches_warehouse(row.get("warehouseName"), keywords)]
    print(f"    Всего строк поступлений: {total}. "
          f"По складам Удмуртии: {len(filtered)}.")
    return filtered


def daterange_windows(date_from: dt.date, date_to: dt.date,
                      window_days: int) -> Iterable[tuple]:
    cur = date_from
    step = dt.timedelta(days=window_days - 1)
    one_day = dt.timedelta(days=1)
    while cur <= date_to:
        end = min(cur + step, date_to)
        yield cur, end
        cur = end + one_day


def fetch_acceptance(client: WBClient, date_from: dt.date, date_to: dt.date,
                     income_ids: set) -> List[Dict[str, Any]]:
    """
    Отчёт о платной приёмке за период, разбитый на окна <= 31 дня.
    Оставляем только записи, относящиеся к поставкам в Удмуртию (по incomeId).
    """
    print(f"[2/2] Запрашиваю отчёт о приёмке (акты) "
          f"{date_from} .. {date_to} ...")
    collected: List[Dict[str, Any]] = []
    for win_from, win_to in daterange_windows(date_from, date_to,
                                              ACCEPTANCE_WINDOW_DAYS):
        params = {
            "dateFrom": win_from.isoformat(),
            "dateTo": win_to.isoformat(),
        }
        print(f"    окно {win_from} .. {win_to}")
        data = client.get(ANALYTICS_BASE, ACCEPTANCE_PATH, params)
        report = data.get("report", []) if isinstance(data, dict) else []
        for row in report:
            # Привязка к Удмуртии — по incomeId из отфильтрованных поступлений.
            if not income_ids or row.get("incomeId") in income_ids:
                collected.append(row)
        # Бережём лимит запросов между окнами.
        time.sleep(1)
    print(f"    Записей приёмки, относящихся к Удмуртии: {len(collected)}.")
    return collected


def build_summary(incomes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Сводка по поставкам: одна строка на поставку (incomeId) со списком артикулов."""
    by_income: Dict[Any, Dict[str, Any]] = {}
    for row in incomes:
        key = row.get("incomeId")
        agg = by_income.setdefault(key, {
            "incomeId": key,
            "number": row.get("number"),
            "warehouseName": row.get("warehouseName"),
            "date": row.get("date"),
            "dateClose": row.get("dateClose"),
            "articles": set(),
            "barcodes": set(),
            "nmIds": set(),
            "total_quantity": 0,
        })
        if row.get("supplierArticle"):
            agg["articles"].add(str(row["supplierArticle"]))
        if row.get("barcode"):
            agg["barcodes"].add(str(row["barcode"]))
        if row.get("nmId"):
            agg["nmIds"].add(str(row["nmId"]))
        agg["total_quantity"] += row.get("quantity", 0) or 0

    summary = []
    for agg in by_income.values():
        summary.append({
            "incomeId": agg["incomeId"],
            "number": agg["number"],
            "warehouseName": agg["warehouseName"],
            "date": agg["date"],
            "dateClose": agg["dateClose"],
            "articles_count": len(agg["articles"]),
            "articles": ", ".join(sorted(agg["articles"])),
            "barcodes": ", ".join(sorted(agg["barcodes"])),
            "nmIds": ", ".join(sorted(agg["nmIds"])),
            "total_quantity": agg["total_quantity"],
        })
    summary.sort(key=lambda r: str(r.get("date") or ""))
    return summary


def write_csv(path: str, rows: List[Dict[str, Any]], columns: List[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_excel(path: str, sheets: List[tuple]) -> None:
    wb = Workbook()
    wb.remove(wb.active)
    for title, rows, columns in sheets:
        ws = wb.create_sheet(title=title[:31])
        ws.append(columns)
        for cell in ws[1]:
            cell.font = Font(bold=True)
        for row in rows:
            ws.append([row.get(c, "") for c in columns])
        # Автоширина по содержимому (с потолком).
        for i, col in enumerate(columns, start=1):
            width = max([len(str(col))] +
                        [len(str(r.get(col, ""))) for r in rows[:200]])
            ws.column_dimensions[get_column_letter(i)].width = min(width + 2, 70)
        ws.freeze_panes = "A2"
    wb.save(path)


INCOME_COLUMNS = ["incomeId", "number", "date", "dateClose", "warehouseName",
                  "supplierArticle", "techSize", "barcode", "nmId",
                  "quantity", "totalPrice", "lastChangeDate"]
SUMMARY_COLUMNS = ["incomeId", "number", "warehouseName", "date", "dateClose",
                   "articles_count", "articles", "barcodes", "nmIds",
                   "total_quantity"]
ACCEPTANCE_COLUMNS = ["giCreateDate", "shkCreateDate", "incomeId", "nmID",
                      "subjectName", "count", "total"]


def parse_date(value: str) -> dt.date:
    return dt.datetime.strptime(value, "%Y-%m-%d").date()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Выгрузка поставок и приёмок ВБ по складам Удмуртии (Ижевск).")
    parser.add_argument("--date-from", required=True,
                        help="Начало периода, ГГГГ-ММ-ДД.")
    parser.add_argument("--date-to",
                        default=dt.date.today().isoformat(),
                        help="Конец периода, ГГГГ-ММ-ДД (по умолчанию сегодня).")
    parser.add_argument("--warehouse", action="append", default=None,
                        help="Ключевое слово склада (можно несколько раз). "
                             "По умолчанию: Ижевск/Удмуртия.")
    parser.add_argument("--out", default="udmurtia_wb_export",
                        help="Префикс имён выходных файлов.")
    parser.add_argument("--no-acceptance", action="store_true",
                        help="Не запрашивать отчёт о приёмке.")
    args = parser.parse_args()

    token = os.environ.get("WB_API_TOKEN")
    if not token:
        raise SystemExit(
            "Не задан WB_API_TOKEN. Возьмите ключ в ЛК: Настройки -> Доступ к "
            "API (категории «Статистика» и «Аналитика») и выполните:\n"
            '    export WB_API_TOKEN="ваш_токен"')

    keywords = [k.lower() for k in (args.warehouse or DEFAULT_WAREHOUSE_KEYWORDS)]
    date_from = parse_date(args.date_from)
    date_to = parse_date(args.date_to)
    if date_to < date_from:
        raise SystemExit("--date-to раньше --date-from.")

    print(f"Период: {date_from} .. {date_to}")
    print(f"Склады (по вхождению): {', '.join(keywords)}\n")

    client = WBClient(token)

    incomes = fetch_incomes(client, date_from.isoformat(), keywords)
    # incomes отдаёт всё с dateFrom; дополнительно ограничим верхнюю границу.
    incomes = [r for r in incomes
               if str(r.get("date", ""))[:10] <= date_to.isoformat()]

    summary = build_summary(incomes)
    income_ids = {r.get("incomeId") for r in incomes if r.get("incomeId")}

    acceptance: List[Dict[str, Any]] = []
    if not args.no_acceptance:
        try:
            acceptance = fetch_acceptance(client, date_from, date_to, income_ids)
        except SystemExit as e:
            print(f"    Предупреждение: отчёт о приёмке не получен ({e}).",
                  file=sys.stderr)

    # --- Запись результатов ---
    csv_income = f"{args.out}_postavki_detail.csv"
    csv_summary = f"{args.out}_postavki_svodka.csv"
    csv_accept = f"{args.out}_priemka_akty.csv"

    write_csv(csv_income, incomes, INCOME_COLUMNS)
    write_csv(csv_summary, summary, SUMMARY_COLUMNS)
    write_csv(csv_accept, acceptance, ACCEPTANCE_COLUMNS)

    print(f"\nCSV сохранены:\n  {csv_summary}\n  {csv_income}\n  {csv_accept}")

    if HAVE_OPENPYXL:
        xlsx = f"{args.out}.xlsx"
        write_excel(xlsx, [
            ("Поставки (сводка)", summary, SUMMARY_COLUMNS),
            ("Поставки (детально)", incomes, INCOME_COLUMNS),
            ("Приёмка (акты)", acceptance, ACCEPTANCE_COLUMNS),
        ])
        print(f"Excel сохранён:\n  {xlsx}")
    else:
        print("\nopenpyxl не установлен — Excel пропущен. "
              "Установите: pip install openpyxl")

    print(f"\nИтого: поставок (incomeId) — {len(summary)}, "
          f"строк поступлений — {len(incomes)}, "
          f"записей приёмки — {len(acceptance)}.")
    if not incomes:
        print("Поступлений по складам Удмуртии за период не найдено. "
              "Проверьте период и что поставки на Ижевск действительно были.")


if __name__ == "__main__":
    main()
