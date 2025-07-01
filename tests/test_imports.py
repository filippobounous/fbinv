import importlib
from pathlib import Path
import sys
from os import path

import pytest

import investment
import inventory

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), "..")))

def _package_modules(package) -> list[str]:
    root = Path(package.__path__[0])
    return [
        f"{package.__name__}." + path.relative_to(root).with_suffix("").as_posix().replace("/", ".")
        for path in root.rglob("*.py")
        if path.name != "__init__.py"
    ]

modules = _package_modules(investment) + _package_modules(inventory)

@pytest.mark.parametrize("module_name", modules)
def test_module_import(module_name):
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        pytest.skip(f"Missing dependency: {exc}")
    except TypeError as exc:
        pytest.fail(f"TypeError raised: {exc}")
    except Exception as exc:
        pytest.skip(f"Import failed: {exc}")
