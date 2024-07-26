import matplotlib.pyplot as plt
import networkx as nx
import re

# List of machines with their respective inputs, outputs, item types, and child machine names
machines = [
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

    ("Miner2", 0, 60, "Copper Ore", ["Smelter3"]),
    ("Smelter3", 30, 30, "Copper Ingot", ["Storage4"]),
    ("Storage4", 30, 30, "Copper Ingot", ["Constructor5", "Constructor6"]),
    ("Constructor5", 15, 30, "Copper Wire", ["Storage5"]),
    ("Constructor6", 15, 30, "Copper Wire", ["Storage5"]),
    ("Storage5", 30, 60, "Copper Wire", [])
]

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

# Automatically define subsets by layers using BFS
def assign_layers(G, start_nodes):
    layers = {}
    queue = []
    for start in start_nodes:
        layers[start] = 0
        queue.append(start)
    
    while queue:
        current = queue.pop(0)
        current_layer = layers[current]
        for neighbor in G.neighbors(current):
            if neighbor not in layers:
                layers[neighbor] = current_layer + 1
                queue.append(neighbor)
    return layers

# Find all nodes that contain 'Miner' in their names
pattern = re.compile(r'Miner')
start_nodes = [node for node in G.nodes if pattern.search(node)]

# Check if any nodes matched
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
pos = nx.multipartite_layout(G, subset_key='layer')  # Use multipartite layout with layers as partitions

# Increase the size of the figure
plt.figure(figsize=(14, 10))

# Define edge colors based on efficiency
edge_colors = [
    'red' if d['efficiency'] < 100 else 'black' for u, v, d in G.edges(data=True)
]

# Draw the graph using nx.draw to include arrows
nx.draw(
    G, pos, with_labels=False, node_size=2500, node_color='lightblue', font_size=10,
    edge_color=edge_colors, linewidths=1, arrows=True, arrowsize=20, arrowstyle='-|>', connectionstyle='arc3,rad=0'
)

# Draw the edge labels with efficiency values
edge_labels = {(u, v): f'{d["efficiency"]:.2f}%' for u, v, d in G.edges(data=True)}
# Adjust edge label positions with some offset to reduce overlap
nx.draw_networkx_edge_labels(
    G, pos, edge_labels=edge_labels, font_size=10, 
    label_pos=0.5, bbox=dict(facecolor='white', alpha=0.5)  # Semi-transparent background
)

# Draw the node labels with both machine names and item types
node_labels = {n: f'{n}\n({machine_dict[n][2]})' for n in G.nodes}
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, verticalalignment='center')

# Show the plot
plt.title("Production Chain: Miner to Storage with Efficiency Ratings and Item Types")
plt.show()
