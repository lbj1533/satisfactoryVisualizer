import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import re

# Define the machine data for different graphs
machines_list = [
    [
        ("Miner1", 0, 60, "Iron Ore", ["Smelter1", "Smelter2"]),
        ("Smelter1", 30, 30, "Iron Ingot", ["Constructor1"]),
        ("Smelter2", 30, 30, "Iron Ingot", ["Constructor2", "Constructor3"]),
        ("Constructor1", 30, 20, "Iron Plate", ["Storage1"]), 
        ("Storage1", 20, 20, "Iron Plate", []),
        ("Constructor2", 15, 15, "Iron Rod", ["Storage2"]),
        ("Constructor3", 15, 15, "Iron Rod", ["Constructor4"]),
        ("Storage2", 15, 15, "Iron Rod", []),
        ("Constructor4", 10, 40, "Screw", ["Storage3"]),
        ("Storage3", 40, 40, "Screw", []),
    ],
    [
        ("Miner2", 0, 60, "Copper Ore", ["Smelter3"]),
        ("Smelter3", 30, 30, "Copper Ingot", ["Storage4"]),
        ("Storage4", 30, 30, "Copper Ingot", ["Constructor5", "Constructor6"]),
        ("Constructor5", 15, 30, "Copper Wire", ["Storage5"]),
        ("Constructor6", 15, 30, "Copper Wire", ["Storage5"]),
        ("Storage5", 30, 60, "Copper Wire", [])
    ],
    [
        ("Miner3", 0, 30, "Limestone", ["Storage6"]),
        ("Storage6", 30, 30, "Limestone", ["Constructor7"]),
        ("Constructor7", 45, 15, "Concrete", ["Storage7"]),
        ("Storage7", 15, 15, "Concrete", [])
    ]
]

def create_graph(machines):
    # Create a dictionary from the list of machines for easy access
    machine_dict = {name: (input_amt, output_amt, item_type, children) for name, input_amt, output_amt, item_type, children in machines}

    # Function to calculate efficiencies based on machine data
    def calculate_efficiencies(machine_dict):
        efficiencies = {}
        for name, (input_amt, output_amt, item_type, children) in machine_dict.items():
            total_used = 0
            for child_name in children:
                # Find the amount used by this child machine from its input
                child_input = machine_dict[child_name][0]
                total_used += child_input
            efficiency = (total_used / output_amt) * 100 if output_amt > 0 else 0
            efficiencies[name] = efficiency
        return efficiencies

    # Calculate efficiencies
    efficiencies = calculate_efficiencies(machine_dict)

    # Create a directed graph and add edges with calculated efficiency as a label
    G = nx.DiGraph()
    for name, (input_amt, output_amt, item_type, children) in machine_dict.items():
        for child_name in children:
            G.add_edge(name, child_name, efficiency=efficiencies[name], item_type=item_type)

    return G, machine_dict

def plot_graph(ax, G, machine_dict, title):
    # Assign layers using DFS
    def assign_layers(G, start_nodes):
        layers = {}
        visited = set()

        def dfs(node, current_layer):
            if node in visited:
                return
            visited.add(node)
            layers[node] = current_layer
            for neighbor in G.neighbors(node):
                if neighbor not in visited:
                    dfs(neighbor, current_layer + 1)

        for start in start_nodes:
            if start not in visited:
                dfs(start, 0)
        
        return layers

    # Find all nodes that contain 'Miner' in their names
    pattern = re.compile(r'Miner')
    start_nodes = [node for node in G.nodes if pattern.search(node)]

    if start_nodes:
        layers = assign_layers(G, start_nodes)
    else:
        raise ValueError("No nodes found matching the pattern 'Miner'")

    # Transform layers dictionary into a dictionary of lists
    layer_dict = {}
    for node, layer in layers.items():
        if layer not in layer_dict:
            layer_dict[layer] = []
        layer_dict[layer].append(node)

    # Set node attributes for layers
    nx.set_node_attributes(G, layers, 'layer')

    # Define the layout of the graph
    pos = nx.multipartite_layout(G, scale=0.7, align="horizontal", subset_key='layer')

    # Define edge colors based on efficiency
    edge_colors = [
        'red' if d['efficiency'] < 100 else 'black' for u, v, d in G.edges(data=True)
    ]

    # Draw the graph using nx.draw to include arrows
    nx.draw(
        G, pos, ax=ax, with_labels=False, node_size=2500, node_color='lightblue', font_size=10,
        edge_color=edge_colors, linewidths=1, arrows=True, arrowsize=20, arrowstyle='-|>', connectionstyle='arc3,rad=0'
    )

    # Draw the edge labels with efficiency values
    edge_labels = {(u, v): f'{d["efficiency"]:.0f}%' for u, v, d in G.edges(data=True) if d["efficiency"] < 100}
    edge_label_positions = {edge: (np.array(pos[edge[0]]) + np.array(pos[edge[1]])) / 2 for edge in G.edges if G[edge[0]][edge[1]]["efficiency"] < 100}

    nx.draw_networkx_edge_labels(
        G, pos, ax=ax, edge_labels=edge_labels, font_size=10, 
        label_pos=0.5, bbox=dict(facecolor='white', alpha=0.5)  # Semi-transparent background
    )

    # Draw the node labels with both machine names and item types
    node_labels = {n: f'{n}\n({machine_dict[n][2]})' for n in G.nodes}
    nx.draw_networkx_labels(G, pos, ax=ax, labels=node_labels, font_size=10, verticalalignment='center')

    # Set the title for the plot
    ax.set_title(title)

def graph_title(data:dict):
    first_key = next(iter(data))
    first_value = data[first_key]
    third_item = first_value[2]
    return f"{third_item} {first_key}"

# Create graphs for all machines
graphs = [create_graph(machines) for machines in machines_list]

# Plot all graphs in separate subplots
fig, axs = plt.subplots(1, len(graphs), figsize=(16, 8))

for ax, (G, machine_dict) in zip(axs, graphs):
    plot_graph(ax, G, machine_dict, graph_title(machine_dict))

plt.tight_layout()
plt.show()
