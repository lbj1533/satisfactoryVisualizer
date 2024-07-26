from typing import List
import matplotlib.pyplot as plt
import networkx as nx

def draw_tree(root):
    G = nx.DiGraph()

    # A dictionary to store nodes by unique identifiers
    node_objects = {}
    node_colors = {}

    def add_edges(node, parent_id=None, depth=0):
        node_id = f"{node.name}_{id(node)}"
        node_objects[node_id] = node
        G.add_node(node_id, subset=depth)  # Set the subset attribute for the node
        if parent_id:
            G.add_edge(parent_id, node_id)
        for child in node.children:
            add_edges(child, node_id, depth + 1)

    add_edges(root)

    # Create node labels and determine node colors
    labels = {}
    for node in G.nodes:
        machine = node_objects[node]
        if machine.name == "Storage":
            labels[node] = machine.name
            node_colors[node] = "lightgrey"  # Color for Storage nodes
        else:
            inputs_str = ", ".join(str(stack) for stack in machine.inputs)
            outputs_str = ", ".join(str(stack) for stack in machine.outputs)
            efficiency_str = f"Efficiency: {machine.output_efficiency:.2f}%"
            
            # Apply color based on efficiency
            if machine.output_efficiency < 100:
                node_colors[node] = "red"
            else:
                node_colors[node] = "lightblue"

            labels[node] = f"{machine.name}\nInputs: [{inputs_str}]\nOutputs: [{outputs_str}]\n{efficiency_str}"

    pos = nx.multipartite_layout(G, subset_key="subset")

    plt.figure(figsize=(12, 8))
    nx.draw(
        G,
        pos,
        with_labels=False,  # We handle labels separately
        node_size=4000,
        node_color=[node_colors[node] for node in G.nodes],  # Apply node colors
        font_size=8,
        font_weight="bold",
        arrows=True,
        edge_color="gray"
    )

    # Manually add labels
    for node, (x, y) in pos.items():
        plt.text(x, y, labels[node],
                 fontsize=6,
                 ha='center',
                 va='center',
                 weight='bold')

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
        self.output_efficiency = 0  # Initialize output efficiency

        # Calculate efficiency after initializing children
        self.calculate_output_efficiency()

    def __str__(self, indent: int = 0) -> str:
        indent_str = "| " * indent
        inputs_str = ", ".join(str(stack) for stack in self.inputs)
        outputs_str = ", ".join(str(stack) for stack in self.outputs)
        output_efficiency_str = f"Efficiency: {self.output_efficiency:.2f}%"

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
            + f"{indent_str}{output_efficiency_str}\n"
            + f"{indent_str}{children_str}"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def add_child(self, machine: "Machine") -> "Machine":
        self.children.append(machine)
        # Recalculate efficiency whenever a child is added
        self.calculate_output_efficiency()
        return self

    def add_line(self, machines: List["Machine"]) -> "Machine":
        current = self
        for machine in machines:
            current.add_child(machine)
            current = machine
        return self
    
    def calculate_output_efficiency(self) -> None:
        total_output = sum(stack.count for stack in self.outputs)
        if total_output == 0:
            self.output_efficiency = 0
        else:
            total_used = 0
            for child in self.children:
                total_used += self._calculate_child_input_efficiency(child)
            
            self.output_efficiency = (total_used / total_output) * 100
        
        # Recur for children
        for child in self.children:
            child.calculate_output_efficiency()

    def _calculate_child_input_efficiency(self, child):
        total_used = 0
        for output in self.outputs:
            for child_input in child.inputs:
                if child_input.item == output.item:
                    total_used += min(child_input.count, output.count)
        
        # If the child is a storage, calculate its children's input efficiency
        if child.name == "Storage":
            for grandchild in child.children:
                total_used += self._calculate_child_input_efficiency(grandchild)
        
        return total_used

def main():
    iron1 = Machine("Miner", None, [Stack(60, "Iron Ore")]).add_child(
        Machine(
            "Smelter", [Stack(30, "Iron Ore")], [Stack(30, "Iron Ingot")]
        ).add_child(
            Machine(
                "Constructor", [Stack(30, "Iron Ingot")], [Stack(20, "Iron Plate")]
            ).add_child(Machine("Storage", [Stack(20, "Iron Plate")]))
        )
    ).add_child(Machine("Storage", None, [Stack(30, "Iron Ore")]).add_child(
        Machine("Smelter", [Stack(30, "Iron Ore")], [Stack(30, "Iron Ingot")])
        .add_child(
            Machine(
                "Constructor", [Stack(15, "Iron Ingot")], [Stack(15, "Iron Rod")]
            ).add_child(Machine("Storage", [Stack(15, "Iron Rod")]))
        )
        .add_child(
            Machine(
                "Constructor", [Stack(15, "Iron Ingot")], [Stack(15, "Iron Rod")]
            ).add_child(
                Machine(
                    "Constructor", [Stack(10, "Iron Rod")], [Stack(40, "Screw")]
                ).add_child(Machine("Storage", [Stack(40, "Screw")]))
            )
        )
    ))

    draw_tree(iron1)

if __name__ == "__main__":
    main()
