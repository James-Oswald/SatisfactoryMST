"""
This script loads the resources json file with the funny layout into networkx graph and caches it
"""

import sys
import json
import matplotlib.pyplot as plt
import networkx as nx

if __name__ == '__main__':
    
    #Load resource node data, naming scheme in this file is quite strange
    with open('resources.json') as f:
        data = json.load(f)

    resource_nodes = None 
    for tab in data["options"]:
        if "tabId" in tab and tab["tabId"] == "resource_nodes":
            resource_nodes = tab["options"]
    
    G = nx.Graph()
    positions = {} #Dictionary to store positions of nodes to pass to drawing
    node_colors = [] #List to store colors of nodes to pass to drawing
    node_sizes = [] #List to store sizes of nodes to pass to drawing

    for resource_node_class in resource_nodes:
        for resource_node_subclass in resource_node_class["options"]:
            for resource_node in resource_node_subclass["markers"]:
                id = resource_node["pathName"].split("BP_ResourceNode")[-1]
                pos = (resource_node["x"], resource_node["y"])
                G.add_node(id, pos=pos) #image=resource_icon)
                positions[id] = (resource_node["x"], -resource_node["y"])
                node_colors.append(resource_node_subclass["insideColor"])
                node_sizes.append(10)
    
    #Add our home base
    base_id = "Base"
    base_pos = (90000, -20000)
    G.add_node(base_id, pos=base_pos) #Add a node at the origin to make the graph connected
    positions[base_id] = base_pos
    node_sizes.append(100)
    node_colors.append("Blue")

    if len(sys.argv) > 1 and sys.argv[1] == "plotNodes":
        img = plt.imread("map.png")
        fig, ax = plt.subplots()
        ax.imshow(img, extent=[-325000, 425000, -375000, 375000])
        nx.draw(G, positions, ax, node_color=node_colors, node_size=10)
        plt.show()
        exit(0)

    #connect all nodes with an edge weighting based on their distance
    for node1 in G.nodes:
        for node2 in G.nodes:
            if node1 == node2:
                continue
            dist = (G.nodes[node1]["pos"][0] - G.nodes[node2]["pos"][0])**2 + (G.nodes[node1]["pos"][1] - G.nodes[node2]["pos"][1])**2
            G.add_edge(node1, node2, weight=dist)

    mst = nx.minimum_spanning_tree(G)
    
    img = plt.imread("map.png")
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[-325000, 425000, -375000, 375000])
    nx.draw(mst, positions, ax, node_color=node_colors, node_size=node_sizes, edge_color='cyan', width=0.5)
    #plt.show()
    plt.savefig("optimized_route.png")
    exit(0)