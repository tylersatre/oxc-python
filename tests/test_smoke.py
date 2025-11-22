import importlib


def test_import_oxc_python():
    mod = importlib.import_module("oxc_python")
    assert hasattr(mod, "__version__")
