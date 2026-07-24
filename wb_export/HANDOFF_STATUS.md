# HANDOFF — статус выгрузки WB по Удмуртии (для локального продолжения)

Самодостаточная записка для продолжения работы в **локальной** среде (напр.
новая сессия Claude Code на ноутбуке). Не требует git-истории — всё нужное
описано здесь. Дата: 2026-07-24.

## Задача

Документально подтвердить (запрос госорганов) поставки / товарооборот,
связанные с **Удмуртской Республикой**. Склады WB там — **«Ижевск»** и
**«Сарапул»**. Нужно выгрузить из ЛК WB:
1. поставки с датами и артикулами на эти склады;
2. акты о приёмке (в т.ч. PDF-документы).

## Что уже сделано (готово и проверено)

Папка `wb_export/` (лежит локально у пользователя, напр.
`C:\Users\Stepan\Downloads\wb_export\`):

| Файл | Назначение |
|------|-----------|
| `wb_udmurtia_export.py` | основной скрипт выгрузки |
| `wb_ping.py` | диагностика доступа токена (JWT-области, статусы эндпоинтов) |
| `show_config_keys.py` | показывает структуру CONFIG.py (значения маскируются) |
| `README.md` | как запускать, все флаги |
| `requirements.txt` | `requests`, `openpyxl` |

Скрипт `wb_udmurtia_export.py` умеет:
- **Поставки (incomes)** — `GET https://statistics-api.wildberries.ru/api/v1/supplier/incomes?dateFrom=…`; фильтр складов по словам `ижевск/izhevsk/сарапул/sarapul/удмурт`; листы «Поставки (сводка)» и «(детально)».
- **Приёмка** — `GET https://seller-analytics-api.wildberries.ru/api/v1/analytics/acceptance-report` окнами ≤31 дня, дедуп, привязка к Удмуртии по `incomeId`.
- **Акты-документы (PDF/ZIP)** по флагу `--download-acts` — API документов `https://documents-api.wildberries.ru`: `/api/v1/documents/list` (постранично, ≤50) + `/api/v1/documents/download` (base64). Категория ключа «Документы». Документы НЕ фильтруются по складу — сопоставлять к Удмуртии по дате/`incomeId`.
- Токен из окружения `WB_API_TOKEN` **или** из `CONFIG.py` через `--config` + `--config-key` (умеет доставать `…wb.headers.Authorization`).
- Вывод: `<out>.xlsx` (3–4 листа) + CSV; с `--download-acts` — папка `<out>_acts/`.
- Переопределение адресов для тестов: `WB_STATISTICS_BASE`, `WB_ANALYTICS_BASE`, `WB_DOCUMENTS_BASE`.

## Конфиг токена (структура CONFIG.py пользователя)

CONFIG.py: `C:\Users\Stepan\Yandex.Disk\WB\ПРОГРАММЫ\PycharmProjects\CONFIG.py`

Токен WB (mag1, RU) лежит как значение заголовка Authorization:
```
credentials.RU.mag1.wb.headers.Authorization   (строка, ~416 символов)
```
Есть также `credentials.RU.mag2`, `credentials.KZ.mag1`.

## ⛔ ТЕКУЩИЙ БЛОКЕР — 404 на incomes

Запуск:
```powershell
python wb_udmurtia_export.py --date-from 2023-01-01 --date-to 2024-12-31 --download-acts `
  --config "C:\Users\Stepan\Yandex.Disk\WB\ПРОГРАММЫ\PycharmProjects\CONFIG.py" `
  --config-key credentials.RU.mag1.wb.headers.Authorization `
  --out "C:\Users\Stepan\Downloads\udmurtia_wb_export"
```

Токен грузится, WB отвечает (сеть и авторизация в порядке, НЕ 401), но:
```
Неожиданный ответ 404 от https://statistics-api.wildberries.ru/api/v1/supplier/incomes
{ "title": "path not found", "origin": "s2s-api-auth-stat", "status": 404,
  "detail": "Please consult the https://dev.wildberries.ru/openapi/api-information" }
```

### Рабочая гипотеза
Токен валиден, но **не имеет доступа к нужному пути**. Наиболее вероятно —
у mag1-токена **нет категории «Статистика»** (WB на нехватку категории отдаёт
404 «path not found», а не 403), либо токен «песочница»/ограниченный, либо
эндпоинт статистики для этого аккаунта изменился к середине 2026.

## ▶ СЛЕДУЮЩИЙ ШАГ — диагностика (сделать первым делом)

Запустить из папки `wb_export`:
```powershell
python wb_ping.py --config "C:\Users\Stepan\Yandex.Disk\WB\ПРОГРАММЫ\PycharmProjects\CONFIG.py" `
  --config-key credentials.RU.mag1.wb.headers.Authorization
```
Он печатает (без раскрытия токена):
- JWT-поля токена: `s` (маска категорий), `exp` (срок), `sandbox`/`t` (тестовый);
- статусы запросов к `common-api /ping` и `/seller-info`, `statistics-api /ping` и `/supplier/incomes`, `seller-analytics /ping`, `documents /categories`.

**Как читать результат:**
- `seller-info` = 200, а `incomes` = 404 → у токена нет категории «Статистика».
  → В ЛК: **Настройки → Доступ к API** — включить категории **Статистика,
  Аналитика, Документы** (перевыпустить токен, обновить CONFIG.py). Учтите:
  токен используется и другими программами пользователя — лучше **добавить**
  категории к текущему, а не сужать.
- `sandbox: true` в JWT → это песочный токен; нужен боевой.
- `exp` в прошлом → токен истёк, перевыпустить.
- Все 200, кроме incomes → уточнить актуальный путь по
  https://dev.wildberries.ru/openapi/ (раздел «Statistics»/«Поставки»).

## Полезные команды

```powershell
# только структура CONFIG.py (значения маскируются):
python show_config_keys.py "C:\...\CONFIG.py"

# список категорий документов в кабинете:
python wb_udmurtia_export.py --date-from 2024-01-01 --list-doc-categories `
  --config "C:\...\CONFIG.py" --config-key credentials.RU.mag1.wb.headers.Authorization
```

## Важно (для органов)

Данные берутся ТОЛЬКО из кабинета пользователя по его ключу. Ничего не
выдумывать: пустой ответ API → пустой отчёт. Подписанные PDF-акты, если нужны
именно заверенные, — из раздела документов ЛК/через `/documents/download`.

## Git (если понадобится)

Ветка `claude/wb-deliveries-ur-export-rtdj6g` в `van-stepan/cian_project`,
папка `wb_export/`. Но всё нужное уже есть локально — git не обязателен.
