# -*- coding: utf-8 -*-
"""Показывает структуру ключей CONFIG.py, чтобы найти правильный путь к
WB-токену для параметра --config-key основного скрипта.

Значения-строки МАСКИРУЮТСЯ (печатается только длина), поэтому вывод безопасно
прислать/показать — сам токен не раскрывается.

Запуск:
    python show_config_keys.py "C:\\Users\\Stepan\\...\\CONFIG.py"
"""
import importlib.util
import os
import sys
import types


def load_module(path: str):
    if os.path.isdir(path):
        path = os.path.join(path, "CONFIG.py")
    if not os.path.isfile(path):
        raise SystemExit(f"CONFIG не найден: {path}")
    spec = importlib.util.spec_from_file_location("cfg_inspect", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Не удалось прочитать {path}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mask(value) -> str:
    if isinstance(value, str):
        return f"<str len={len(value)}>"
    if isinstance(value, (list, tuple, set)):
        return f"<{type(value).__name__} len={len(value)}>"
    return f"<{type(value).__name__}>"


def walk(obj, prefix: str) -> None:
    if isinstance(obj, dict):
        for key in obj.keys():
            child = obj[key]
            path = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(child, dict):
                print(f"  {path}   (dict, keys: {list(child.keys())})")
                walk(child, path)
            else:
                print(f"  {path} = {mask(child)}")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            'Использование: python show_config_keys.py "путь\\к\\CONFIG.py"')
    module = load_module(sys.argv[1])

    print("Верхнеуровневые переменные CONFIG.py:\n")
    found = False
    for name in sorted(dir(module)):
        if name.startswith("_"):
            continue
        val = getattr(module, name)
        if callable(val) or isinstance(val, types.ModuleType):
            continue
        found = True
        if isinstance(val, dict):
            print(f"{name}   (dict, keys: {list(val.keys())})")
            walk(val, name)
        else:
            print(f"{name} = {mask(val)}")
    if not found:
        print("(словарей/строк верхнего уровня не найдено)")
    print("\nНужен путь до строки-токена, например: credentials.ru.mag1.wb")
    print("Его и передайте основному скрипту как --config-key <путь>.")


if __name__ == "__main__":
    main()
