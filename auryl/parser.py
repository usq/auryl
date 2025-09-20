from typing import Iterable, List
from lark import Lark, visitors
from pathlib import Path

import lark

from auryl.error import TypeNotFoundError
from auryl.tree import (
    CompTree,
    Component,
    Input,
    Node,
    Output,
    Package,
    Primitive,
    Type,
    Datum,
)


class ScopeHandler:
    def __init__(self, comp_tree: CompTree) -> None:
        self.comp_tree = comp_tree
        self.current_scope: Node = self.comp_tree.root

    def enter_package(self, package_fqn: List[str]) -> None:
        package_target = package_fqn[:]
        while package_target:
            p = package_target.pop(0)
            if new_scope := self.current_scope.lookup(p):
                self.current_scope = new_scope
            else:
                self.current_scope = self.current_scope.add_child(Package(_name=p))

    def add_new_scope(self, new_scope: Node) -> None:
        self.current_scope = self.current_scope.add_child(new_scope)

    def pop_scope(self) -> None:
        new_scope = self.current_scope.parent
        assert new_scope
        self.current_scope = new_scope

    def get_type(self, type_name: str) -> Type:
        if type_name == "int":
            return Primitive.INT
        raise TypeNotFoundError(type_name)


class AstVisitor(visitors.Interpreter):

    def __init__(self, comp_tree: CompTree) -> None:
        self.scope = ScopeHandler(comp_tree)

    def package_decl(self, tree: lark.Tree) -> None:
        ident = str(tree.children[0])
        self.scope.enter_package(ident.split("."))

    def component(self, tree: lark.Tree):
        comp_name, contents = tree.children[0], tree.children[1:]
        component = Component(_name=str(comp_name))
        self.scope.add_new_scope(component)
        for cont in contents:
            assert isinstance(cont, lark.Tree)
            self.visit(cont)
        self.scope.pop_scope()

    def input(self, tree: lark.Tree) -> None:
        input_name, type_name = tree.children[0], tree.children[1]
        inputs = self.scope.current_scope.lookup("in")
        assert inputs
        type_ = self.scope.get_type(str(type_name))
        inputs.add_child(Input(_name=str(input_name), type_=type_))

    def output(self, tree: lark.Tree) -> None:
        output_name, type_name = tree.children[0], tree.children[1]
        outputs = self.scope.current_scope.lookup("out")
        assert outputs
        type_ = self.scope.get_type(str(type_name))
        outputs.add_child(Output(_name=str(output_name), type_=type_))

    def datum(self, tree: lark.Tree) -> None:
        datum_name, type_name = tree.children[0], tree.children[1]
        data = self.scope.current_scope.lookup("data")
        assert data
        type_ = self.scope.get_type(str(type_name))
        data.add_child(Datum(_name=str(datum_name), type_=type_))


def parse(files: Iterable[Path]) -> CompTree:

    parser = Lark(Path("auryl/grammar.lark").read_text())

    comp_tree = CompTree()
    for file in files:
        tree = parser.parse(file.read_text())
        AstVisitor(comp_tree).visit(tree)

    return comp_tree
