from typing import List
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

def draw_tree(root):
    G = nx.DiGraph()
    
    # A dictionary to store nodes by unique identifiers
    node_objects = {}

    def add_edges(node, parent_id=None):
        node_id = f"{node.name}_{id(node)}"
        node_objects[node_id] = node
        if parent_id:
            G.add_edge(parent_id, node_id)
        for child in node.children:
            add_edges(child, node_id)
    
    add_edges(root)
    
    # Create node labels with inputs and outputs
    labels = {}
    for node in G.nodes:
        machine = node_objects[node]
        inputs_str = ", ".join(str(stack) for stack in machine.inputs)
        outputs_str = ", ".join(str(stack) for stack in machine.outputs)
        labels[node] = f"{machine.name}\nInputs: [{inputs_str}]\nOutputs: [{outputs_str}]"
    
    pos = nx.spectral_layout(G)
    
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=2000, node_color="lightblue", font_size=10, font_weight="bold", arrows=True)
    plt.show()

class Stack:
    def __init__(self, count: int, item: str) -> None:
        self.count = count
        self.item = item

    def __str__(self) -> str:
        return f"{self.count}x {self.item}"

class Machine:
    def __init__(
        self,
        name: str = "Machine",
        inputs: List[Stack] = None,
        outputs: List[Stack] = None,
        children: List["Machine"] = None,
    ) -> None:
        self.name = name
        self.inputs = [] if inputs is None else inputs
        self.outputs = [] if outputs is None else outputs
        self.children = [] if children is None else children

    def __str__(self, indent: int = 0) -> str:
        indent_str = "| " * indent
        inputs_str = ", ".join(str(stack) for stack in self.inputs)
        outputs_str = ", ".join(str(stack) for stack in self.outputs)

        # Handle the case where there are no children
        if self.children:
            children_str = "\n".join(
                child.__str__(indent + 1) for child in self.children
            )
        else:
            children_str = "\n"  # Default to newline if no children

        # Compute the length for the dashes
        max_len = max(len(inputs_str), len(outputs_str), len(children_str))
        dash_line = f"{' -' * min(20, 8 + max_len)}\n"

        green = "\033[32m"
        bright_blue = "\033[94m"
        magenta = "\033[35m"
        reset = "\033[0m"

        return (
            dash_line
            + f"{indent_str}{bright_blue}{self.name}{reset}\n"
            + f"{indent_str}{green}Inputs: [{inputs_str}]{reset}\n"
            + f"{indent_str}{magenta}Outputs: [{outputs_str}]{reset}\n"
            + f"{indent_str}{children_str}"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def add_child(self, machine: "Machine") -> "Machine":
        self.children.append(machine)
        return self

    def add_line(self, machines: List["Machine"]) -> "Machine":
        current = self
        for machine in machines:
            current.add_child(machine)
            current = machine
        return self

def main():
    iron1: Machine = Machine("Miner", None, [Stack(60, "Iron Ore")]).add_child(
        Machine(
            "Smelter", [Stack(30, "Iron Ore")], [Stack(30, "Iron Ingot")]
        ).add_child(
            Machine(
                "Constructor", [Stack(30, "Iron Ingot")], [Stack(20, "Iron Plate")]
            ).add_child(Machine("Storage", [Stack(20, "Iron Plate")]))
        )
    )
    print(f"* Iron 1{iron1}")

    iron2: Machine = Machine("Storage", None, [Stack(30, "Iron Ore")]).add_child(
        Machine("Smelter", [Stack(30, "Iron Ore")], [Stack(30, "Iron Ingot")])
        .add_child(
            Machine(
                "Constructor", [Stack(15, "Iron Ingot")], [Stack(15, "Iron Rod")]
            ).add_child(Machine("Storage", [Stack(15, "Iron Rod")]))
        )
        .add_child(
            Machine("Constructor", [Stack(15, "Iron Ingot")], [Stack(15, "Iron Rod")]).add_child(
            Machine("Constructor", [Stack(10, "Iron Rod")], [Stack(40, "Screw")]).add_child(Machine("Storage", [Stack(40, "Screw")]))
        ))
            
    )

    print(f"* Iron 2{iron2}")

    draw_tree(iron1)
    draw_tree(iron2)

if __name__ == "__main__":
    main()
