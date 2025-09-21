from typing import Iterable, List, Optional
from lark import Lark, visitors
from pathlib import Path

import lark

from auryl.error import TypeNotFoundError
from auryl.tree import (
    CompTree,
    Component,
    Runnables,
    Input,
    InputTrigger,
    Node,
    Output,
    Package,
    Primitive,
    Ref,
    Runnable,
    RunnableOutput,
    Trigger,
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

    def lookup(self, *fqn: str) -> Optional[Node]:
        return self.lookup_in(self.current_scope, *fqn)

    def lookup_in(self, node: Node, *fqn:str) -> Optional[Node]:
        if new_node := node.lookup(fqn[0]):
            return node.lookup(*fqn)
        if p := node.parent:
            return self.lookup_in(p, *fqn)
        return None


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

    def runnables(self, tree: lark.Tree) -> None:
        self.scope.add_new_scope(Runnables(_name="run"))
        for c in tree.children:
            self.visit(c)
        self.scope.pop_scope()


    def run(self, tree: lark.Tree) -> None:
        runnable_name, children = tree.children[0], tree.children[1:]
        print("parsing run named", runnable_name)
        run = Runnable(_name=runnable_name)
        self.scope.add_new_scope(run)
        print(f"Runnabel parent is now: {run.parent}")
        for c in children:
            self.visit(c)
        self.scope.pop_scope()

    def run_trigger(self, tree: lark.Tree) -> None:
        trigger_name = str(tree.children[0]).split(".")
        inp = self.scope.lookup(*trigger_name)
        assert inp
        trigger = InputTrigger(Ref(to_node=inp))
        assert isinstance(self.scope.current_scope, Runnable)
        self.scope.current_scope.trigger.append(trigger)

    def run_output(self, tree: lark.Tree) -> None:
        output_name = str(tree.children[0]).split(".")
        out = RunnableOutput()
        assert isinstance(self.scope.current_scope, Runnable)
        self.scope.current_scope.output.append(out)

def parse(files: Iterable[Path]) -> CompTree:

    parser = Lark(Path("auryl/grammar.lark").read_text())

    comp_tree = CompTree()
    for file in files:
        tree = parser.parse(file.read_text())
        AstVisitor(comp_tree).visit(tree)

    return comp_tree
