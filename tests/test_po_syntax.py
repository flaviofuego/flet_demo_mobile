import py_compile
from pathlib import Path


def test_po_py_compiles():
    po_path = Path(__file__).resolve().parents[1] / "po.py"
    py_compile.compile(str(po_path), doraise=True)
