import pytest
import tempfile
from auryl import parser,tree
from pathlib import Path


def test_empty_component(tmpdir):

    testfile = Path(tmpdir / "file1.aur")

    testfile.write_text("""
    package bar.biz;
    comp foo{}
    """)

    system = parser.parse([testfile])
    package = system.root.lookup("bar", "biz")
    assert isinstance(package, tree.Package)

    component = package.lookup("foo")
    assert isinstance(component, tree.Component)



def test_full_component(tmpdir):
    testfile = Path(tmpdir / "file1.aur")

    testfile.write_text("""
    package bar.biz;
    comp foo{
       in {
         a: int;
       }
    }
    """)

    system = parser.parse([testfile])
    foo = system.root.lookup("bar", "biz", "foo")
    assert foo
    a = foo.lookup("in", "a")
    assert a
    assert isinstance(a, tree.Input)



def test_imports(tmpdir):
    ...
