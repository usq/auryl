from os import system
from lark import Lark, visitors
from pathlib import Path


class Visitor(visitors.Interpreter):
    def component(self,tree):
        print("found component")
        # self.visit(tree.children[0])
        comp_name, contentes = tree.children[0], tree.children[1]
        self.visit(contentes)
        print("tree:", tree)

    def content(self, tree):
        print("Parse content")
        print(tree)

def parse():
    system("ls")
    parser = Lark(Path("auryl/grammar.lark").read_text())
    tree = parser.parse("comp Foo {abc}")
    print(Visitor().visit(tree))
