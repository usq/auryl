import pytest
import tempfile
from auryl import parser
from pathlib import Path


def test_init(tmpdir):

    testfile = Path(tmpdir / "file1.aur")

    testfile.write_text("""
    package bar;
    comp foo{}
    """)

    parser.parse([testfile])


