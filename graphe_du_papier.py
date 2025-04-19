def construct_gp(p):
    """
    Construct the base graph Gp as described in the paper:
    - 2^p lower level vertices: (lower, 0) to (lower, 2^p - 1)
    - 2^p - 1 upper level vertices: (upper, 0) to (upper, 2^p - 2)
    - Each triangle connects two consecutive lower nodes with one upper node.
    - All edges have cost 1.
    """
    gp = {}  # Dictionary to represent the graph
    num_lower = 2 ** p
    num_upper = 2 ** p - 1

    # Add lower level nodes
    for i in range(num_lower):
        gp[("lower", i)] = {}

    # Add upper level nodes
    for i in range(num_upper):
        gp[("upper", i)] = {}

    # Add triangle edges
    for i in range(num_upper):
        left = ("lower", i)
        right = ("lower", i + 1)
        upper = ("upper", i)

        gp[left][upper] = 1
        gp[upper][left] = 1
        gp[upper][right] = 1
        gp[right][upper] = 1
        gp[left][right] = 1
        gp[right][left] = 1

    return gp


def construct_gp_plus(p):
    gp = construct_gp(p)
    gp_plus = {node: neighbors.copy() for node, neighbors in gp.items()}
    all_nodes = list(gp_plus.keys())

    u = "u"
    gp_plus[u] = {}
    blocked_edges = set()

    # Add edges from u to all other nodes (weight 1, blocked)
    for v in all_nodes:
        gp_plus[u][v] = 1
        gp_plus[v][u] = 1
        # Sort the tuple lexicographically based on string representation
        edge = tuple(sorted([str(u), str(v)], key=str))
        blocked_edges.add(edge)

    # Update list of nodes
    all_nodes.append(u)

    # Add new edges (not from u, not already in the original gp, weight 2, blocked)
    for i in range(len(all_nodes)):
        for j in range(i + 1, len(all_nodes)):
            n1 = all_nodes[i]
            n2 = all_nodes[j]

            # Skip if either node is u
            if u in [n1, n2]:
                continue
            # Skip if the edge already exists in the original Gp
            if n2 in gp.get(n1, {}):
                continue
            # Add a new blocked edge (weight 2)
            gp_plus[n1][n2] = 2
            gp_plus[n2][n1] = 2
            # Sort the tuple lexicographically based on string representation
            edge = tuple(sorted([str(n1), str(n2)], key=str))
            blocked_edges.add(edge)
    
    
    # --- Print blocked edges ---
    # print("\n" + "=" * 60)
    # print("BLOCKED EDGES".center(60))
    # print("=" * 60)
    # sorted_edges = sorted(blocked_edges, key=lambda e: (str(e[0]), str(e[1])))
    # for edge in sorted_edges:
    #     weight = gp_plus[edge[0]][edge[1]]
    #     print(f"{edge[0]} -- {edge[1]}  (cost: {weight})")
    # print("=" * 60 + "\n")

    start_node = ("lower", 0)
    return gp_plus, start_node, blocked_edges


def print_graph(G):
    """
    Print the graph G for easy readability

    Args:
        G (dict): The graph to be printed
    """
    print("\n" + "=" * 80)
    print("GRAPH G".center(80))
    print("=" * 80)
    
    nodes_by_level = {"lower": [], "upper": [], "other": []}
    for node in G:
        if isinstance(node, tuple):
            level = node[0]
            if level in nodes_by_level:
                nodes_by_level[level].append(node)
            else:
                nodes_by_level["other"].append(node)
        else:
            nodes_by_level["other"].append(node)
    
    total_nodes = sum(len(nodes) for nodes in nodes_by_level.values())
    total_edges = sum(len(neighbors) for neighbors in G.values()) // 2
    print(f"\nTotal number of nodes: {total_nodes}")
    print(f"Total number of edges: {total_edges}")
    
    for level in ["lower", "upper", "other"]:
        if nodes_by_level[level]:
            print(f"\n{'-' * 40}")
            print(f"NODES AT LEVEL {level.upper()}:")
            print(f"{'-' * 40}")
            
            # Sort nodes lexicographically
            sorted_nodes = sorted(nodes_by_level[level], key=lambda x: str(x))
            
            # Print details for each node
            for node in sorted_nodes:
                neighbors = list(G[node].keys())
                # Sort neighboring nodes in order
                sorted_neighbors = sorted(neighbors, key=lambda x: str(x))
                # Calculate the total weight of the edges
                total_weight = sum(G[node][n] for n in neighbors)
                
                print(f"\nNode: {node}")
                print("  List of neighboring nodes:")
                for n in sorted_neighbors:
                    weight = G[node][n]
                    print(f"    - {n} (weight: {weight})")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    p = 3
    gp = construct_gp(p)
    # print_graph(gp)
    gp_plus, start_node, blocked = construct_gp_plus(p)
    print_graph(gp_plus)

    # print("Start Node:", start_node)
    # print("Graph Nodes:")
    # for node, neighbors in gp_plus.items():
    #     print(f"  {node} -> {list(neighbors.keys())}")
