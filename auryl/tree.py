from __future__ import annotations
from dataclasses import field, dataclass
from typing import Dict, Generic, List, Optional, Tuple, TypeVar, Union, Sequence
from enum import Enum


T = TypeVar("T")

class Ref(Generic[T]):
    def __init__(self, *, to_node: Optional[Node], to_ref: Sequence[str] = ()) -> None:
        self.to = to_node

class Primitive(Enum):
    INT = 1

class ComplexRef:
    def __init__(self, ident:str):
        self.ident = ident

Type = Union[Primitive, ComplexRef]

class CompVisitor(Generic[T]):
    def stop(self):
        self._stopped = True

    def visit_node(self, node: Node) -> T:
        ...

    def visit_root_node(self, root: RootNode) -> T:
        return self.visit_node(root)

    def visit_package(self, package: Package) -> T:
        return self.visit_node(package)

    def visit_component(self, component: Component) -> T:
        return self.visit_node(component)

VisitorT = TypeVar("VisitorT", bound=CompVisitor)

@dataclass(kw_only=True)
class Node:
    _name: str

    _parent: Optional[Ref[Node]] = None
    _children: List[Node] = field(default_factory=list)
    _children_map: Dict[str, Tuple[int, Ref[Node]]] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self._name

    def lookup(self, *path:str) -> Optional[Node]:
        first, rest = path[0], path[1:]
        if child_entry := self._children_map.get(first):
            if rest:
                node = child_entry[1].to
                assert node
                return node.lookup(*rest)
            return child_entry[1].to
        return None


    @property
    def children(self) -> List[Node]:
        return self._children[:]

    @name.setter
    def set_name(self, value: str):
        self._name = value

    def add_child(self, child: Node) -> Node:
        if child.name in self._children_map:
            if self._children_map[child.name][1].to is child:
                raise ValueError(f"Child {child.name} is already child of {self.name}")
            raise ValueError(f"Node {self.name} already has child with name {child.name}, but it's a different node")
        self._children.append(child)
        self._children_map[child.name] = (len(self._children)-1, Ref(to_node=child))
        child._parent = Ref(to_node=self)
        return child

    def remove_child(self, child_name: str) -> Node:
        if child_name not in self._children_map:
            raise ValueError(f"Node {child_name} is not a child of {self.name}")
        idx, child = self._children_map[child_name]
        return self._children.pop(idx)

    def get_root(self) -> Optional[Node]:
        if self._parent is None:
            return None
        return self._parent.to.get_root()

    @property
    def is_root(self) -> bool:
        return False

    @property
    def parent(self) -> Optional[Node]:
        if self._parent:
            return self._parent.to
        return None

    def accept(self, visitor: CompVisitor[T]) -> T:
        return visitor.visit_node(self)

    def walk_df_pre(self, visitor: VisitorT) -> VisitorT:
        to_visit:List[Node] = [self]
        while(to_visit):
            c = to_visit.pop()
            c.accept(visitor)
            if children_ := c.children:
                to_visit.extend(reversed(children_))

        return visitor;

    def walk_bf_pre(self, visitor: VisitorT) -> VisitorT:
        self.accept(visitor)
        to_visit = self._children[:]
        while to_visit:
            c = to_visit.pop(0)
            c.accept(visitor)
            to_visit.extend(c.children)
        return visitor


@dataclass
class RootNode(Node):
    def get_root(self) -> Optional[Node]:
        return self

    def lookup(self, *path:str) -> Optional[Node]:
        first, rest = path[0], path[1:]
        if first == self._name:
            if rest:
                return super().lookup(*rest)
            return self
        return super().lookup(*path)


    @property
    def is_root(self) -> bool:
        return True

    def accept(self, visitor: CompVisitor[T]) -> T:
        return visitor.visit_root_node(self)

@dataclass
class Package(Node):
    def accept(self, visitor: CompVisitor[T]) -> T:
        return visitor.visit_package(self)

@dataclass
class Inputs(Node):
    ...

@dataclass
class Outputs(Node):
    ...

@dataclass
class Data(Node):
    ...

@dataclass
class Runnables(Node):
    ...


@dataclass
class Component(Node):
    def __post_init__(self) -> None:
        self.add_child(Inputs(_name="in"))
        self.add_child(Outputs(_name="out"))
        self.add_child(Data(_name="data"))

    def accept(self, visitor: CompVisitor[T]) -> T:
        return visitor.visit_component(self)


@dataclass
class Input(Node):
    type_: Type

@dataclass
class Output(Node):
    type_: Type

@dataclass
class Datum(Node):
    type_: Type

@dataclass
class Runnable(Node):
    trigger: List[Trigger] = field(default_factory=list)
    output: List[RunnableOutput] = field(default_factory=list)

@dataclass
class Trigger:
    ...

@dataclass
class InputTrigger(Trigger):
    triggered_by: Ref[Input]


@dataclass
class RunnableOutput:
    write_to: Ref[Output]

class CompTree:
    def __init__(self):
        self.root = RootNode(_name="Root")

