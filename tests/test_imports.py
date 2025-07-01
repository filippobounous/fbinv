"""Tests that all project modules can be imported without TypeError."""

import importlib
from pathlib import Path
import sys
from os import path
import unittest

# Ensure project root is on the import path
sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), "..")))

import investment
import inventory


def _package_modules(package) -> list[str]:
    """Return a list of all module paths within *package*."""

    root = Path(package.__path__[0])
    return [
        (
            f"{package.__name__}."
            + file_path.relative_to(root)
            .with_suffix("")
            .as_posix()
            .replace("/", ".")
        )
        for file_path in root.rglob("*.py")
        if file_path.name != "__init__.py"
    ]


modules = _package_modules(investment) + _package_modules(inventory)


class TestModuleImports(unittest.TestCase):
    """Container for dynamically generated import tests."""

    pass


def _make_test(module_name: str):
    """Create a test function that imports *module_name*."""

    def test(self) -> None:
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            raise unittest.SkipTest(f"Missing dependency: {exc}")
        except TypeError as exc:
            self.fail(f"TypeError raised: {exc}")
        except Exception as exc:
            raise unittest.SkipTest(f"Import failed: {exc}")

    return test


for _module in modules:
    test_name = "test_" + _module.replace(".", "_")
    setattr(TestModuleImports, test_name, _make_test(_module))


if __name__ == "__main__":
    unittest.main()
