from typing import Iterable, List
from lark import Lark, visitors
from pathlib import Path

import lark

from auryl.tree import CompTree, Component, Node, Package


class ScopeHandler:
    def __init__(self, comp_tree: CompTree) -> None:
        self.comp_tree = comp_tree
        self.current_scope: Node = self.comp_tree.root

    def enter_package(self, package_fqn: List[str]) -> None:
        package_target = package_fqn[:]
        while(package_target):
            p = package_target.pop(0)
            if new_scope := self.current_scope.lookup(p):
                self.current_scope = new_scope
            else:
                self.current_scope = self.current_scope.add_child(Package(p))
    def add_new_scope(self, new_scope: Node) -> None:
        self.current_scope = self.current_scope.add_child(new_scope)

    def pop_scope(self) -> None:
        new_scope = self.current_scope.parent
        assert new_scope
        self.current_scope = new_scope


class AstVisitor(visitors.Interpreter):
    def __init__(self, comp_tree: CompTree) -> None:
        self.scope = ScopeHandler(comp_tree)

    def package_decl(self, tree: lark.Tree) -> None:
        ident = str(tree.children[0])
        self.scope.enter_package(ident.split("."))

    def component(self,tree):
        comp_name, contents = tree.children[0], tree.children[1:]
        component = Component(comp_name)
        self.scope.add_new_scope(component)
        # for cont in contents:
        #     self.visit(cont)
        self.scope.pop_scope()

def parse(files: Iterable[Path]) -> CompTree:

    parser = Lark(Path("auryl/grammar.lark").read_text())

    comp_tree = CompTree()
    for file in files:
        tree = parser.parse(file.read_text())
        AstVisitor(comp_tree).visit(tree)

    return comp_tree
