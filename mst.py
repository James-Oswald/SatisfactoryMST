"""
This script drives the generation of the minimum spanning tree
"""

#Standard Libs
import sys
import json
import argparse

#External Libs
import networkx as nx
import matplotlib.pyplot as plt

if __name__ == '__main__':

    #Parse the various command line arguments
    parser = argparse.ArgumentParser(
        prog="Satisfactory MST",
        description=f"Computes a minimum spanning tree for all\
                      resource nodes with various options",
    )
    parser.add_argument('filename') 
    parser.add_argument(
        "-d", "--distance_measure", 
        choices=["l2_xy", "l2_xyz", "l1_xy", "l1_xyz"],
        default='l2_xyz',
        help=f"The distance measure to use for the MST.\n\
               l1 is taxicab distance, l2 is euclidean distance.\n\
               xy to ignore heights of nodes, xyz takes hights into account."
    )
    parser.add_argument(
        "-b", "--base_cords", 
        nargs='+',
        type=int,
        help=f"x y (z) cords of your base, will be included in the MST as a big blue dot"
    )
    parser.add_argument(
        "-x", "--headless", 
        help=f"don't display the figure in a matplotlib window at the end.",
        action="store_true"
    )
    parser.add_argument(
        "-o", "--output", 
        type=str,
        help=f"output path to save the mst image to a file."
    )

    args = parser.parse_args(sys.argv)

    #Small input validation for base cords
    if args.base_cords is not None and not 2 <= len(args.base_cords) <= 3:
        print(f"Expected either two or three base cords, got {len(args.base_cords)}")
        exit(1)
    
    #add a default z dimension if only two cords are provided
    if args.base_cords is not None and len(args.base_cords) == 2:
        args.base_cords.append(0) 

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
                pos = (resource_node["x"], resource_node["y"], resource_node["z"])
                G.add_node(id, pos=pos) 
                positions[id] = (resource_node["x"], -resource_node["y"])
                node_colors.append(resource_node_subclass["insideColor"])
                node_sizes.append(10)
    
    #If specified, add home base at specified cords
    if args.base_cords is not None:
        base_id = "Base"
        base_pos = args.base_cords
        base_pos[1] = -base_pos[1] #Need to flip y cord for display
        G.add_node(base_id, pos=base_pos) #Add a node at the origin to make the graph connected
        positions[base_id] = base_pos[0:2]
        node_sizes.append(80)
        node_colors.append("Blue")

    #connect all nodes with an edge weighting based on their distance
    for node1 in G.nodes:
        for node2 in G.nodes:
            if node1 == node2:
                continue
            if args.distance_measure == "l2_xyz":
                dist = (G.nodes[node1]["pos"][0] - G.nodes[node2]["pos"][0])**2 + \
                       (G.nodes[node1]["pos"][1] - G.nodes[node2]["pos"][1])**2 + \
                       (G.nodes[node1]["pos"][2] - G.nodes[node2]["pos"][2])**2
            elif args.distance_measure == "l2_xy":
                dist = (G.nodes[node1]["pos"][0] - G.nodes[node2]["pos"][0])**2 + \
                       (G.nodes[node1]["pos"][1] - G.nodes[node2]["pos"][1])**2
            elif args.distance_measure == "l1_xyz":
                dist = abs(G.nodes[node1]["pos"][0] - G.nodes[node2]["pos"][0]) + \
                       abs(G.nodes[node1]["pos"][1] - G.nodes[node2]["pos"][1]) + \
                       abs(G.nodes[node1]["pos"][2] - G.nodes[node2]["pos"][2])
            elif args.distance_measure == "l1_xy":
                dist = abs(G.nodes[node1]["pos"][0] - G.nodes[node2]["pos"][0]) + \
                       abs(G.nodes[node1]["pos"][1] - G.nodes[node2]["pos"][1])
            G.add_edge(node1, node2, weight=dist)

    #compute MST
    mst = nx.minimum_spanning_tree(G)
    
    #Draw MST image
    img = plt.imread("map.png")
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[-325000, 425000, -375000, 375000])
    nx.draw(mst, positions, ax, node_color=node_colors, node_size=node_sizes, edge_color='cyan', width=0.5)
    
    if args.headless is None:
        plt.show()
    if args.output is not None:
        plt.savefig(args.output)
    
    exit(0)