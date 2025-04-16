import numpy as np
from christofides import apply_christophides
from utils import transform_to_matrix, get_path_in_letters,get_blockages_in_int
from scipy.sparse import csr_array
from scipy.sparse.csgraph import dijkstra
import sys 

MAX_INT = sys.maxsize


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
        G_star[u][v] = MAX_INT
        G_star[v][u] = MAX_INT
    
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


    visited_vertices = list(set(range(n)) - set(Us[1:]))  # V \ Us we don't take in account the 0 
    print(visited_vertices)

    visited_vertices.append(3)

    print(list(sorted(visited_vertices)))
    [0,1,2,3,4,5,6]
    {0,2,3,5}
    
    [0,1,4,6]

    [0,1,2,4,5,6]
    [0,1,2,3,4,5]

    [0,1,3,4,5,6]
    [0,1,2,3,4,5]
    for i in range(len(Us)):
        u = Us[i]

        
        for j in range(i + 1, len(Us)):
            v = Us[j]

            tmp_visited = visited_vertices + [v] 
            if i != 0: tmp_visited += [u]
            tmp_visited = list(sorted(tmp_visited)) # TRES IMPORTANT pour garder les poids dand l'ordre 

            mini_graph = [G_star[ligne] for ligne in tmp_visited]

            # v et a quelle index ? 2 ok alor mini graph 2 
            # les deux indices ne sont pas visité donc leurs poids va être mis a MAX car 
            # on veut pas qu'il prend ce chemin pour le Djistra on veut que des chemins qui ont été visité 
            if i != 0:
                mini_graph[i,j] = MAX_INT
                mini_graph[j,i] = MAX_INT

            dist_matrix, predecessors = dijkstra(csgraph=csr_array(G_star), directed=False, indices=u, return_predecessors=True)

            
            
            G_star[u,v] = dist_matrix[v] # 0. 1. 2. 1. 1.]
            G_star[v,u] = dist_matrix[v]
    
        
    
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
                
        if next_vertex == -1:break
            
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
    
    # Get initial TSP tour using Christofides
    christophides_path = apply_christophides(matrix)
    path_in_letters = get_path_in_letters(christophides_path, routes)
    blockages = get_blockages_in_int(blockages,routes)
    

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
        ["D", "E"],["E","D"]
    ]

    final_path = apply_cnn_to_routes(routes, blockages)
    #print(f"Path: {final_path}")

