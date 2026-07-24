# -*- coding: utf-8 -*-
"""
Выгрузка поставок и приёмок по складам Wildberries в Удмуртии
(склады «Ижевск» и «Сарапул»).

Скрипт ходит в официальные API Wildberries под вашим API-ключом и собирает:
  1. Поступления/поставки на склад (incomes) — дата, склад, артикул, баркод,
     nmId, количество, дата приёмки. Это и есть подтверждение того, что товар
     был поставлен и принят на складе ВБ в Удмуртии.
  2. Отчёт о платной приёмке (acceptance-report / «акты о приёмке»), привязанный
     к поставкам в Удмуртию по incomeId.
  3. (опционально, --download-acts) сами документы-акты о приёмке в PDF/ZIP
     через API документов.

Результат — файл Excel (несколько листов) + CSV-копии, а с --download-acts
ещё и папка <out>_acts/ со скачанными файлами актов.

Данные берутся ТОЛЬКО из вашего собственного кабинета продавца по вашему ключу.
Ничего не выдумывается: если API вернёт пусто — в отчёте будет пусто.

Использование:
    export WB_API_TOKEN="ваш_токен_из_ЛК"      # Настройки -> Доступ к API
    python3 wb_udmurtia_export.py --date-from 2023-01-01 --date-to 2024-12-31
    # с актами-документами:
    python3 wb_udmurtia_export.py --date-from 2023-01-01 --download-acts

Токен должен иметь доступ к категориям «Статистика» и «Аналитика», а для
скачивания актов-документов — ещё и «Документы».
"""

import argparse
import base64
import csv
import datetime as dt
import os
import re
import sys
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter
    HAVE_OPENPYXL = True
except ImportError:  # Excel-вывод опционален; CSV пишется всегда.
    HAVE_OPENPYXL = False


# --- Эндпоинты официального API Wildberries ---------------------------------
# Базовые адреса можно переопределить через окружение (удобно для тестов
# против локального мок-сервера); по умолчанию — боевые адреса WB.
STATISTICS_BASE = os.environ.get(
    "WB_STATISTICS_BASE", "https://statistics-api.wildberries.ru")
ANALYTICS_BASE = os.environ.get(
    "WB_ANALYTICS_BASE", "https://seller-analytics-api.wildberries.ru")
DOCUMENTS_BASE = os.environ.get(
    "WB_DOCUMENTS_BASE", "https://documents-api.wildberries.ru")

INCOMES_PATH = "/api/v1/supplier/incomes"                    # поступления на склад
ACCEPTANCE_PATH = "/api/v1/analytics/acceptance-report"      # платная приёмка
DOC_CATEGORIES_PATH = "/api/v1/documents/categories"         # категории документов
DOC_LIST_PATH = "/api/v1/documents/list"                     # список документов
DOC_DOWNLOAD_PATH = "/api/v1/documents/download"             # скачать один документ

# Ключевые слова для отбора складов Удмуртии. Склады WB в республике —
# «Ижевск» и «Сарапул». Сравнение регистронезависимое, по вхождению подстроки.
DEFAULT_WAREHOUSE_KEYWORDS = ["ижевск", "izhevsk", "сарапул", "sarapul", "удмурт"]

# Ключевые слова для отбора актов о приёмке среди всех документов продавца.
# Документы НЕ фильтруются по складу — приёмку к Удмуртии сопоставляют вручную
# по дате/incomeId через лист «Поставки».
DEFAULT_ACT_KEYWORDS = ["приёмк", "приемк", "acceptance"]

# Ограничение окна для отчёта приёмки (API принимает интервалы <= 31 дня).
ACCEPTANCE_WINDOW_DAYS = 31

# Максимум строк на страницу в списке документов (ограничение API).
DOC_LIST_PAGE_LIMIT = 50


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
    seen = set()  # защита от повторов на границах окон
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
            if income_ids and row.get("incomeId") not in income_ids:
                continue
            key = (row.get("incomeId"), row.get("nmID"),
                   row.get("giCreateDate"), row.get("shkCreateDate"),
                   row.get("count"), row.get("total"))
            if key in seen:
                continue
            seen.add(key)
            collected.append(row)
        # Бережём лимит запросов между окнами.
        time.sleep(1)
    print(f"    Записей приёмки, относящихся к Удмуртии: {len(collected)}.")
    return collected


# --- Документы (акты о приёмке в формате PDF/ZIP) ---------------------------
# API документов: https://documents-api.wildberries.ru, категория ключа
# «Документы». Ответы завёрнуты в {"data": {...}}. Документы НЕ фильтруются по
# складу — акт к Удмуртии сопоставляют по дате/incomeId через лист «Поставки».

def _doc_data(payload: Any) -> Dict[str, Any]:
    return payload.get("data", {}) if isinstance(payload, dict) else {}


def fetch_document_categories(client: WBClient,
                              locale: str = "ru") -> List[Any]:
    payload = client.get(DOCUMENTS_BASE, DOC_CATEGORIES_PATH, {"locale": locale})
    return _doc_data(payload).get("categories", []) or []


def fetch_documents_list(client: WBClient, date_from: dt.date, date_to: dt.date,
                         locale: str = "ru",
                         category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Список документов продавца за период (с постраничной подкачкой)."""
    documents: List[Dict[str, Any]] = []
    offset = 0
    while True:
        params: Dict[str, Any] = {
            "locale": locale,
            "beginTime": date_from.isoformat(),
            "endTime": date_to.isoformat(),
            "limit": DOC_LIST_PAGE_LIMIT,
            "offset": offset,
        }
        if category:
            params["category"] = category
        payload = client.get(DOCUMENTS_BASE, DOC_LIST_PATH, params)
        batch = _doc_data(payload).get("documents", []) or []
        documents.extend(batch)
        if len(batch) < DOC_LIST_PAGE_LIMIT:
            break
        offset += DOC_LIST_PAGE_LIMIT
        time.sleep(2)  # бережём лимит запросов (list: burst 5 / 10 c)
    return documents


def matches_act(doc: Dict[str, Any], keywords: Iterable[str]) -> bool:
    hay = " ".join(str(doc.get(k, "")) for k in
                   ("name", "category", "serviceName")).lower()
    return any(kw in hay for kw in keywords)


def pick_extension(extensions: Optional[List[str]]) -> Optional[str]:
    """Выбираем предпочтительный формат: pdf, затем zip, xlsx, иначе первый."""
    if not extensions:
        return None
    low = {str(e).lower(): str(e) for e in extensions}
    for pref in ("pdf", "zip", "xlsx", "xls"):
        if pref in low:
            return low[pref]
    return str(extensions[0])


def _safe_filename(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|\r\n]+", "_", name).strip()
    return name or "document"


def download_document(client: WBClient, service_name: str,
                      extension: str) -> Tuple[Optional[str], Optional[bytes]]:
    payload = client.get(DOCUMENTS_BASE, DOC_DOWNLOAD_PATH,
                         {"serviceName": service_name, "extension": extension})
    data = _doc_data(payload)
    content_b64 = data.get("document")
    if not content_b64:
        return data.get("fileName"), None
    raw = base64.b64decode(content_b64)
    fname = data.get("fileName") or f"{service_name}.{extension}"
    return fname, raw


DOC_COLUMNS = ["creationTime", "category", "name", "serviceName",
               "extensions", "savedFile"]


def download_acts(client: WBClient, date_from: dt.date, date_to: dt.date,
                  out_prefix: str, keywords: List[str],
                  category: Optional[str] = None,
                  locale: str = "ru") -> List[Dict[str, Any]]:
    """Скачивает акты о приёмке (документы) за период в папку <out>_acts/."""
    print(f"[3/3] Запрашиваю список документов {date_from} .. {date_to} ...")
    docs = fetch_documents_list(client, date_from, date_to, locale, category)
    print(f"    Всего документов за период: {len(docs)}.")
    if category is None:
        docs = [d for d in docs if matches_act(d, keywords)]
        print(f"    Из них похожи на акты приёмки: {len(docs)} "
              f"(по словам: {', '.join(keywords)}).")

    folder = f"{out_prefix}_acts"
    os.makedirs(folder, exist_ok=True)
    manifest: List[Dict[str, Any]] = []
    for doc in docs:
        service_name = doc.get("serviceName")
        ext = pick_extension(doc.get("extensions"))
        saved = ""
        if service_name and ext:
            try:
                fname, raw = download_document(client, service_name, ext)
                if raw:
                    path = os.path.join(folder, _safe_filename(fname))
                    with open(path, "wb") as f:
                        f.write(raw)
                    saved = path
                    print(f"    сохранён: {path}")
            except SystemExit as e:
                print(f"    не удалось скачать {service_name}: {e}",
                      file=sys.stderr)
            time.sleep(2)  # download: burst 5 / 10 c
        manifest.append({
            "creationTime": doc.get("creationTime"),
            "category": doc.get("category"),
            "name": doc.get("name"),
            "serviceName": service_name,
            "extensions": ", ".join(doc.get("extensions") or []),
            "savedFile": saved,
        })
    return manifest


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
                        help="Не запрашивать отчёт о платной приёмке.")
    # --- документы (акты о приёмке в PDF/ZIP) ---
    parser.add_argument("--download-acts", action="store_true",
                        help="Дополнительно скачать акты о приёмке (документы) "
                             "в папку <out>_acts/. Нужен доступ ключа к "
                             "категории «Документы».")
    parser.add_argument("--list-doc-categories", action="store_true",
                        help="Показать категории документов и выйти.")
    parser.add_argument("--list-docs", action="store_true",
                        help="Показать список документов за период и выйти.")
    parser.add_argument("--doc-category", default=None,
                        help="ID категории документов для точного отбора "
                             "(вместо отбора по ключевым словам).")
    parser.add_argument("--acts-keyword", action="append", default=None,
                        help="Ключевое слово для отбора актов приёмки среди "
                             "документов (можно несколько раз). "
                             "По умолчанию: приёмк/приемк/acceptance.")
    parser.add_argument("--doc-locale", default="ru",
                        help="Язык категорий документов (ru/en/zh).")
    args = parser.parse_args()

    token = os.environ.get("WB_API_TOKEN")
    if not token:
        raise SystemExit(
            "Не задан WB_API_TOKEN. Возьмите ключ в ЛК: Настройки -> Доступ к "
            "API (категории «Статистика», «Аналитика», а для актов —\n"
            "«Документы») и выполните:\n"
            '    export WB_API_TOKEN="ваш_токен"')

    keywords = [k.lower() for k in (args.warehouse or DEFAULT_WAREHOUSE_KEYWORDS)]
    act_keywords = [k.lower() for k in (args.acts_keyword or DEFAULT_ACT_KEYWORDS)]
    date_from = parse_date(args.date_from)
    date_to = parse_date(args.date_to)
    if date_to < date_from:
        raise SystemExit("--date-to раньше --date-from.")

    client = WBClient(token)

    # --- Служебные режимы по документам: показать и выйти ---
    if args.list_doc_categories:
        cats = fetch_document_categories(client, args.doc_locale)
        print(f"Категорий документов: {len(cats)}")
        for cat in cats:
            print("  ", cat)
        return
    if args.list_docs:
        docs = fetch_documents_list(client, date_from, date_to,
                                    args.doc_locale, args.doc_category)
        rows = [{
            "creationTime": d.get("creationTime"), "category": d.get("category"),
            "name": d.get("name"), "serviceName": d.get("serviceName"),
            "extensions": ", ".join(d.get("extensions") or []), "savedFile": "",
        } for d in docs]
        out_csv = f"{args.out}_documents.csv"
        write_csv(out_csv, rows, DOC_COLUMNS)
        print(f"Документов за период: {len(docs)}. Список: {out_csv}")
        return

    print(f"Период: {date_from} .. {date_to}")
    print(f"Склады (по вхождению): {', '.join(keywords)}\n")

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

    acts_manifest: List[Dict[str, Any]] = []
    if args.download_acts:
        try:
            acts_manifest = download_acts(client, date_from, date_to, args.out,
                                          act_keywords, args.doc_category,
                                          args.doc_locale)
        except SystemExit as e:
            print(f"    Предупреждение: акты не скачаны ({e}).", file=sys.stderr)

    # --- Запись результатов ---
    csv_income = f"{args.out}_postavki_detail.csv"
    csv_summary = f"{args.out}_postavki_svodka.csv"
    csv_accept = f"{args.out}_priemka_akty.csv"

    write_csv(csv_income, incomes, INCOME_COLUMNS)
    write_csv(csv_summary, summary, SUMMARY_COLUMNS)
    write_csv(csv_accept, acceptance, ACCEPTANCE_COLUMNS)
    print(f"\nCSV сохранены:\n  {csv_summary}\n  {csv_income}\n  {csv_accept}")
    if args.download_acts:
        csv_acts = f"{args.out}_akty_dokumenty.csv"
        write_csv(csv_acts, acts_manifest, DOC_COLUMNS)
        print(f"  {csv_acts}  (+ PDF/ZIP в папке {args.out}_acts/)")

    if HAVE_OPENPYXL:
        xlsx = f"{args.out}.xlsx"
        sheets = [
            ("Поставки (сводка)", summary, SUMMARY_COLUMNS),
            ("Поставки (детально)", incomes, INCOME_COLUMNS),
            ("Приёмка (акты)", acceptance, ACCEPTANCE_COLUMNS),
        ]
        if args.download_acts:
            sheets.append(("Документы (акты)", acts_manifest, DOC_COLUMNS))
        write_excel(xlsx, sheets)
        print(f"Excel сохранён:\n  {xlsx}")
    else:
        print("\nopenpyxl не установлен — Excel пропущен. "
              "Установите: pip install openpyxl")

    print(f"\nИтого: поставок (incomeId) — {len(summary)}, "
          f"строк поступлений — {len(incomes)}, "
          f"записей приёмки — {len(acceptance)}"
          + (f", скачано актов — "
             f"{sum(1 for a in acts_manifest if a.get('savedFile'))}"
             if args.download_acts else "") + ".")
    if not incomes:
        print("Поступлений по складам Удмуртии за период не найдено. Проверьте "
              "период и что поставки на Ижевск/Сарапул действительно были.")


if __name__ == "__main__":
    main()
