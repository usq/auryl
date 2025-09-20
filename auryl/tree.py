from __future__ import annotations
from dataclasses import field, dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class Node:
    _name: str
    _parent: Optional[Node] = None
    _children: List[Node] = field(default_factory=list)
    _children_map: Dict[str, Tuple[int, Node]] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def set_name(self, value: str):
        self._name = value

    def add_child(self, child: Node) -> Node:
        if child.name in self._children_map:
            if self._children_map[child.name][1] is child:
                raise ValueError(f"Child {child.name} is already child of {self.name}")
            raise ValueError(f"Node {self.name} already has child with name {child.name}, but it's a different node")
        self._children.append(child)
        self._children_map[child.name] = (len(self._children)-1, child)
        child._parent = self
        return child

    def remove_child(self, child_name: str) -> Node:
        if child_name not in self._children_map:
            raise ValueError(f"Node {child_name} is not a child of {self.name}")
        idx, child = self._children_map[child_name]
        return self._children.pop(idx)

    def get_root(self) -> Optional[Node]:
        if self._parent is None:
            return None
        return self._parent.get_root()

    @property
    def parent(self) -> Optional[Node]:
        return self._parent

@dataclass
class RootNode(Node):
    def get_root(self) -> Optional[Node]:
        return self

class CompTree:
    def __init__(self):
        self.root = RootNode("Root")

