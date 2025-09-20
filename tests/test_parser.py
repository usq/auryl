import pytest
import tempfile
from auryl import parser,tree
from pathlib import Path


def test_init(tmpdir):

    testfile = Path(tmpdir / "file1.aur")

    testfile.write_text("""
    package bar.biz;
    comp foo{}
    """)

    system = parser.parse([testfile])
    package = system.root.lookup("bar")
    assert isinstance(package, tree.Package)


