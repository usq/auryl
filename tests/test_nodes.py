from auryl.tree import CompVisitor, Component, Node, Package, RootNode

def test_parent_child():
    parent = Node("Parent")
    child = parent.add_child(Node("Child"))
    assert child.parent is parent

    root = RootNode("Root")
    root.add_child(parent)
    assert child.get_root() is root


def test_df_visitor():
    class TrackingVisitor(CompVisitor[None]):
        def __init__(self):
            self.order = []

        def visit_node(self, node: Node) -> None:
            self.order.append(node.name)
    #      a
    # b    c    d
    # e   f g   h
    #
    # df = a,b,e,c,f,g,d,h

    a = Node("a")

    b = a.add_child(Node("b"))
    c = a.add_child(Node("c"))
    d = a.add_child(Node("d"))

    e = b.add_child(Node("e"))
    f = c.add_child(Node("f"))
    g = c.add_child(Node("g"))
    h = d.add_child(Node("h"))


    df_visitor = a.walk_df_pre(TrackingVisitor())
    assert df_visitor.order == ["a", "b", "e", "c", "f", "g", "d", "h"]

    bf_visitor = a.walk_bf_pre(TrackingVisitor())
    assert bf_visitor.order == ["a", "b", "c", "d", "e", "f", "g", "h"]


def test_comp_visit_methods_called():
    root = RootNode("root")
    assert root.is_root
    assert root.get_root() is root

    class TestVisitor(CompVisitor[None]):
        def __init__(self) -> None:
            self.found_package = False
            self.found_component = False

        def visit_package(self, package: Package) -> None:
            self.found_package = True
        def visit_component(self, component: Component) -> None:
            self.found_component = True

    package = root.add_child(Package("p"))
    assert root.walk_bf_pre(TestVisitor()).found_package
    comp = package.add_child(Component("c"))
    assert root.walk_bf_pre(TestVisitor()).found_component

