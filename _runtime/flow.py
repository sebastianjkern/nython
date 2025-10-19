from _runtime.node import NodeData
from _util.diff import diff_dict

import json

class Flow:
    def __init__(self) -> None:
        self.nodes: list[NodeData] = list()

    def save(self):
        with open("./flow.json", "w") as file:
            file.write( json.dumps(self.nodes, default=lambda o: o.to_dict(), indent=4))
       
    @classmethod
    def load(cls):
        with open("./_examples/flow.json", "r") as file:
            read_flow = json.loads(file.read())

        flow = Flow()

        for node in read_flow:
            n = NodeData(node["uuid"], code=node["code"])
            n.children = node["children"]
            n.parents = node["parents"]
            flow.nodes.append(n)

        return flow
    
    def run(self):
        # Execute nodes in topological order.
        remaining = set(self.nodes)
        executed_outputs: dict[NodeData, tuple] = {}

        while remaining:
            for node in list(remaining):
                parents = getattr(node, "parents", [])
                if all(p in executed_outputs for p in parents):
                    if not parents:
                        globals_dict = {}
                        locals_dict = {}
                    else:
                        globals_dict, locals_dict = executed_outputs[parents[0]]


                    # <– execute the node in both cases
                    new_globals, new_locals = node.execute(globals_dict, locals_dict)
                    executed_outputs[node] = (new_globals, new_locals)

                    print(diff_dict(globals_dict, new_globals))
                    print(diff_dict(locals_dict, new_locals))

                    remaining.remove(node)

    def to_python(self) -> str:
        return NotImplemented
                    
if __name__ == "__main__":
    # Create a simple linear dependency A -> B -> C and an independent node D
    node_a = NodeData("A", code="print('Hello, Node A')")
    node_b = NodeData("B", code="print('Hello, Node B'); a = 2")
    node_c = NodeData("C", code="print('Hello, Node C'); a = 4")
    node_d = NodeData("D", code="print('Hello, Node D')")

    node_a.children.append(node_b)
    node_b.parents.append(node_a)

    node_b.children.append(node_c)
    node_c.parents.append(node_b)

    # Node D has no parents and will use builtins as globals
    flow = Flow()
    flow.nodes = [node_a, node_b, node_c, node_d]
    flow.save()
    
    print("Running the flow...")
    flow.run()
    print("Flow execution completed.")

    new_flow = flow.load()
    print("Running the newly read flow...")
    flow.run()
    print("Read Flow execution completed.")
