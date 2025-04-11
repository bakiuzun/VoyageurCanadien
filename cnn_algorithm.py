import numpy as np
from christofides import apply_christophides
from utils import transform_to_matrix, get_path_in_letters

def find_next_vertex_in_order(current_vertex, tour, blockages):
    """
    Find the next vertex in the tour order when encountering a blockage
    """
    n = len(tour)
    current_idx = tour.index(current_vertex)
    
    # Try going to the next vertex
    next_idx = (current_idx + 1) % n
    next_vertex = tour[next_idx]
    
    # If the edge is blocked, try going to the next vertex (undirected graph)
    while [current_vertex, next_vertex] in blockages or [next_vertex, current_vertex] in blockages:
        next_idx = (next_idx + 1) % n
        next_vertex = tour[next_idx]
        
        # If a full cycle is completed without finding a path
        if next_idx == current_idx:
            return None
            
    return next_vertex

def update_edge_knowledge(graph, visited_vertices, blockages, Eb, routes):
    """
    Update knowledge about edges when visiting a new vertex
    - Learn about all edges adjacent to the visited vertex
    - Add blocked edges to Eb
    """
    n = len(graph)
    vertex_idx = visited_vertices[-1]  # The newly visited vertex
    route_keys = list(routes.keys())
    current_vertex_letter = route_keys[vertex_idx]

    # Check all edges adjacent to the vertex
    for i in range(n):
        if i != vertex_idx:
            next_vertex_letter = route_keys[i]
            # Check if edge is blocked
            if [current_vertex_letter, next_vertex_letter] in blockages or [next_vertex_letter, current_vertex_letter] in blockages:
                # Add to Eb if not already there
                if [current_vertex_letter, next_vertex_letter] not in Eb and [next_vertex_letter, current_vertex_letter] not in Eb:
                    # print(f"adding edge to Eb: {current_vertex_letter}-{next_vertex_letter}\n")
                    Eb.append([current_vertex_letter, next_vertex_letter])
            # If edge is not blocked and leads to an unvisited vertex => a valid edge
            elif i not in visited_vertices:
                # We can use this edge in the future
                pass

def create_multigraph(graph, visited_vertices, blockages):
    """
    Create the multigraph G' from unvisited vertices and the starting vertex
    Only use direct edges between vertices
    """
    n = len(graph)
    unvisited = set(range(n)) - set(visited_vertices)
    Us = list(unvisited) + [visited_vertices[0]]  # U union {s}
    
    # Create adjacency matrix for G'
    size = len(Us)
    G_prime = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        G_prime[i][i] = 0

    # print(f"G_prime: {G_prime}")
    
    # Add direct edges
    # for i in range(len(Us)):
    #     for j in range(len(Us)):
    #         if i != j:
    #             # Only add edge if not blocked
    #             if [Us[i], Us[j]] not in blockages:
    #                 G_prime[i][j] = graph[Us[i]][Us[j]]
    
    return G_prime, Us

def nearest_neighbor(graph, start=0):
    n = len(graph)
    visited = [False] * n
    path = [start]
    visited[start] = True
    current = start
    
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
    christophides_path = apply_christophides(matrix)
    path_in_letters = get_path_in_letters(christophides_path, routes)
    
    # Initialize Eb (set of discovered blocked edges)
    Eb = []
    
    # Handle blockages
    first_path = []
    current_vertex = path_in_letters[0]
    first_path.append(current_vertex)
    visited_vertices = [list(routes.keys()).index(current_vertex)]  # Dictionary (key: value) to list index
    
    while len(first_path) < len(path_in_letters):
        next_vertex = find_next_vertex_in_order(current_vertex, path_in_letters, Eb)
        # Update knowledge about edges when visiting a new vertex
        update_edge_knowledge(matrix, visited_vertices, blockages, Eb, routes)

        if next_vertex is None:
            # If no next path is found, go back to the starting vertex
            # by going in reverse
            for vertex in reversed(path_in_letters[1:]):
                if [current_vertex, vertex] not in Eb:
                    first_path.append(vertex)
                    current_vertex = vertex
                    visited_vertices.append(list(routes.keys()).index(vertex))
                    break
            break
            
        # Check if there's a blockage between current_vertex and next_vertex
        if [current_vertex, next_vertex] in Eb or [next_vertex, current_vertex] in Eb:
            # If blocked, try to find another path
            continue
            
        first_path.append(next_vertex)
        current_vertex = next_vertex
        visited_vertices.append(list(routes.keys()).index(next_vertex))
        
        print(f"visited_vertices: {visited_vertices}")
        
        # If we have returned to the starting vertex
        if current_vertex == path_in_letters[0]:
            break

    # Create the multigraph G'
    G_prime, Us = create_multigraph(matrix, visited_vertices, Eb) 
    print(f"G_prime: {G_prime}")
    print(f"Us: {Us}")
    nn_path = nearest_neighbor(G_prime)
    
    # Convert path from G' back to the original graph
    route_keys = list(routes.keys())
    second_path = []
    for idx in nn_path:
        second_path.append(route_keys[Us[idx]])
        
    final_path = first_path + [v for v in second_path if v not in first_path]
    
    return final_path

if __name__ == "__main__":
    routes = {
        'A': {'A':0, 'B': 1, 'C':2,'D': 1,'E':1},
        'B': {'A': 1, 'B':0, 'C':1, 'D': 2, 'E': 1},
        'C': {'A': 2, 'B':1, 'C':0, 'D': 1, 'E': 1},
        'D': {'A': 1, 'B':2, 'C':1, 'D': 0, 'E': 1},
        'E': {'A': 1, 'B':1, 'C':1, 'D': 1, 'E': 0},
    }

    blockages = [
        ["D", "E"] 
    ]

    final_path = apply_cnn_to_routes(routes, blockages)
    print(f"Path: {final_path}")
