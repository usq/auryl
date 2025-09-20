from auryl.tree import CompVisitor, Component, Node, Package, RootNode

def test_parent_child():
    parent = Node(_name="Parent")
    child = parent.add_child(Node(_name="Child"))
    assert child.parent is parent

    root = RootNode(_name="Root")
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

    a = Node(_name="a")

    b = a.add_child(Node(_name="b"))
    c = a.add_child(Node(_name="c"))
    d = a.add_child(Node(_name="d"))

    e = b.add_child(Node(_name="e"))
    f = c.add_child(Node(_name="f"))
    g = c.add_child(Node(_name="g"))
    h = d.add_child(Node(_name="h"))


    df_visitor = a.walk_df_pre(TrackingVisitor())
    assert df_visitor.order == ["a", "b", "e", "c", "f", "g", "d", "h"]

    bf_visitor = a.walk_bf_pre(TrackingVisitor())
    assert bf_visitor.order == ["a", "b", "c", "d", "e", "f", "g", "h"]


def test_comp_visit_methods_called():
    root = RootNode(_name="root")
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

    package = root.add_child(Package(_name="p"))
    assert root.walk_bf_pre(TestVisitor()).found_package
    comp = package.add_child(Component(_name="c"))
    assert root.walk_bf_pre(TestVisitor()).found_component


def test_node_lookup():
    root = RootNode(_name="root")
    a = root.add_child(Node(_name="a"))
    b = a.add_child(Node(_name="b"))

    assert root.lookup("root") is root
    assert root.lookup("root", "a") is a
    assert root.lookup("root", "a", "b") is b

    assert a.lookup("b") is b
    assert a.lookup("a") is None
    assert a.lookup("invalid") is None
