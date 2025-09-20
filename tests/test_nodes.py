from auryl.tree import Node, RootNode

def test_parent_child():
    parent = Node("Parent")
    child = parent.add_child(Node("Child"))
    assert child.parent is parent

    root = RootNode("Root")
    root.add_child(parent)
    assert child.get_root() is root
