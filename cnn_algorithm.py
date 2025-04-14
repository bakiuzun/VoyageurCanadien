import numpy as np
from christofides import apply_christophides
from utils import transform_to_matrix, get_path_in_letters

def find_shortest_path(graph, start, end, visited_vertices):
    """
    Find shortest path from start to end using only edges with at least one visited vertex and not blocked
    """
    n = len(graph)
    dist = [999999] * n
    dist[start] = 0
    visited = [False] * n
    
    while True:
        # Find unvisited vertex with minimum distance
        u = -1
        min_dist = 999999
        for i in range(n):
            if not visited[i] and dist[i] < min_dist:
                min_dist = dist[i]
                u = i
                
        if u == -1 or u == end:
            break
            
        visited[u] = True
        
        # Update distances to neighbors
        for v in range(n):
            if not visited[v] and graph[u][v] != 999999:
                # Only use edges where at least one vertex is visited
                if u in visited_vertices or v in visited_vertices:
                    if dist[u] + graph[u][v] < dist[v]:
                        dist[v] = dist[u] + graph[u][v]
                        
    return dist[end]


def shortcut(graph, tsp_tour, blockages):
    """
    Simulates the journey following a TSP tour and makes shortcuts when blocked edges are encountered.
    
    Args:
        graph: Weight matrix of the graph
        tsp_tour: Order of vertices in the TSP tour
        blockages: List of blocked edges
        
    Returns:
        tuple: (G_star, U, P1) - the visited graph, unvisited vertices, and the shortcut path
    """
    num_nodes = len(graph)
    G_star = np.copy(graph)
    U = {tsp_tour[0]}
    P1 = [tsp_tour[0]]
    Eb = set()

    i = 0
    j = 1

    while j < len(tsp_tour):
        vi = tsp_tour[i]
        vj = tsp_tour[j]

        for x in range(num_nodes):
            if x != vi:
                is_blocked = [vi, x] in blockages or [x, vi] in blockages
                if is_blocked:
                    Eb.add(tuple(sorted((vi, x))))
        is_blocked = [vi, vj] in blockages or [vj, vi] in blockages
        if not is_blocked:
            P1.append(vj)
            i = j
        else:   
            U.add(vj)
        j += 1
    # Check edge back to the starting vertex
    is_blocked = [tsp_tour[i], tsp_tour[0]] in blockages or [tsp_tour[0], tsp_tour[i]] in blockages
    if is_blocked:
        # Return using the reverse path
        return_path = P1[::-1][1:]  # Skip the repeated start vertex
        P1.extend(return_path)

    # Update the known graph with blocked edges
    for u, v in Eb:
        G_star[u][v] = 999999
        G_star[v][u] = 999999
    
    # print(G_star)
    # print(U)
    # print(P1)

    return G_star, U, P1

def compress(G_star, U, G):
    """
    Create multigraph G' from G* and U
    For each pair of vertices in U, find shortest path using only known edges
    """
    Us = list(U)  
    n = len(G_star)
    G_prime = [[999999] * n for _ in range(n)]
    
    # Add known edges among Us from G_star
    for u in Us:
        G_prime[u][u] = 0
        for v in Us:
            if u != v and G_star[u][v] != 999999:
                G_prime[u][v] = G_star[u][v]
    # Add compressed edges (via known parts of the graph)
    visited_vertices = set(range(n)) - set(Us)  # V \ Us
    for i in range(len(Us)):
        u = Us[i]
        for j in range(i + 1, len(Us)):
            v = Us[j]
            if G_prime[u][v] == 999999:  # only if not already connected directly
                cost = find_shortest_path(G, u, v, visited_vertices)
                if cost != 999999:
                    G_prime[u][v] = cost
                    G_prime[v][u] = cost  # since undirected

    print(G_prime)
    return G_prime

def nearest_neighbor(graph):
    n = len(graph)
    visited = [False] * n
    path = [0]
    visited[0] = True
    current = 0
    
    while len(path) < n:
        next_vertex = -1
        min_dist = float('inf')
        
        for i in range(n):
            if not visited[i] and graph[current][i] < min_dist:
                min_dist = graph[current][i]
                next_vertex = i
                
        if next_vertex == -1:
            break
            
        path.append(next_vertex)
        visited[next_vertex] = True
        current = next_vertex
        
    return path

def apply_cnn_to_routes(routes, blockages=None):
    """
    Apply the CNN algorithm to the TSP problem
    CNN combines:
    1. Christofides' algorithm to create an initial tour
    2. Handling blockages by following the tour order
    3. Handling unvisited vertices by creating the multigraph G'
    """
    if blockages is None:
        blockages = []
        
    matrix = transform_to_matrix(routes)
    print(matrix)
    
    # Get initial TSP tour using Christofides
    christophides_path = apply_christophides(matrix)
    # path_in_letters = get_path_in_letters(christophides_path, routes)
    
    # Create shortcut path
    G_star, U, P1 = shortcut(matrix, christophides_path, blockages)
    
    # Create compressed graph G'
    G_prime = compress(G_star, U, matrix)

    # P2 = nearest_neighbor(G_prime)
    
    # final_path = P1 + [v for v in P2 if v not in P1]
    
    # return final_path

if __name__ == "__main__":
    routes = {
        'A': {'A':0, 'B': 1, 'C':2,'D': 1,'E':1},
        'B': {'A': 1, 'B':0, 'C':1, 'D': 2, 'E': 1},
        'C': {'A': 2, 'B':1, 'C':0, 'D': 1, 'E': 1},
        'D': {'A': 1, 'B':2, 'C':1, 'D': 0, 'E': 1},
        'E': {'A': 1, 'B':1, 'C':1, 'D': 1, 'E': 0},
    }

    blockages = [
        ["D", "E"],
    ]

    final_path = apply_cnn_to_routes(routes, blockages)
    print(f"Path: {final_path}")
