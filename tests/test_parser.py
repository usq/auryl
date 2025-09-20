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

        out {
          a: int;
        }

        data {
          a: int;
        }

        run {
          process [on in.a; to out.a];
        }
    }
    """)

    system = parser.parse([testfile])
    foo = system.root.lookup("bar", "biz", "foo")
    assert foo
    a_in = foo.lookup("in", "a")
    a_out = foo.lookup("out", "a")
    a_data = foo.lookup("data", "a")
    assert a_in
    assert a_out
    assert a_data
    assert isinstance(a_in, tree.Input)
    assert isinstance(a_out, tree.Output)
    assert isinstance(a_data, tree.Datum)
    assert a_in.type_ == tree.Primitive.INT
    assert a_out.type_ == tree.Primitive.INT
    assert a_data.type_ == tree.Primitive.INT


    runnables = foo.lookup("run")
    assert runnables
    print(runnables)
    print(foo.children)
    proc = runnables.lookup("process")
    assert proc

def test_imports(tmpdir):
    ...
