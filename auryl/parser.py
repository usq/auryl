from os import system
from typing import Iterable
from lark import Lark, visitors
from pathlib import Path

from auryl.tree import CompTree


class Visitor(visitors.Interpreter):
    def __init__(self, comp_tree: CompTree) -> None:
        self.comp_tree = comp_tree

    def component(self,tree):
        print("found component")
        # self.visit(tree.children[0])
        comp_name, contents = tree.children[0], tree.children[1:]
        for cont in contents:

            self.visit(cont)
        print("tree:", tree)

    def content(self, tree):
        print("Parse content")
        print(tree)


def parse(files: Iterable[Path]) -> CompTree:


    parser = Lark(Path("auryl/grammar.lark").read_text())

    comp_tree = CompTree()
    for file in files:
        tree = parser.parse(file.read_text())
        print(Visitor(comp_tree).visit(tree))

    return comp_tree
