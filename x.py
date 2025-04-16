import numpy as np
from christofides import apply_christophides
from utils import transform_to_matrix, get_path_in_letters,get_blockages_in_int
from scipy.sparse import csr_array
from scipy.sparse.csgraph import dijkstra
import sys 

MAX_INT = sys.maxsize


def mapp_predecessor(n,tmp_visited,predecessor):

    mapped_predecessor = np.full(n, -1, dtype=int)  # -1 pour les non-visités
    for k, pred in enumerate(predecessor):
        if pred != -9999:  # -9999 est la valeur par défaut de scipy pour aucun prédécesseur
            mapped_predecessor[tmp_visited[k]] = tmp_visited[pred]      
    return mapp_predecessor

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
    G_prime = [[MAX_INT] * len(Us) for _ in range(len(Us))]

    visited_vertices = list(set(range(n)) - set(Us))  # V \ Us 
    total_predecessors  = []
    for i in range(len(Us)):
        u = Us[i]

        for j in range(i + 1, len(Us)):
            v = Us[j]

            tmp_visited = visited_vertices + [v] 
            tmp_visited += [u]
            if i != 0: tmp_visited += [0]
            tmp_visited = list(sorted(tmp_visited)) # TRES IMPORTANT pour garder les poids dand l'ordre 

            mini_graph = [[G_star[row][col] for col in tmp_visited] for row in tmp_visited]
          
            ind_v = tmp_visited.index(v)
            ind_u = tmp_visited.index(u)

            """
            on veut faire le plus court chemin en utilisant seulement les sommets visité 
            quand on va donner le graph a djistra si on ne met pas la valeur de la distance 
            entre u et v a MAX alors il se peut qu'il utilise ce chemin OR u et v ne sont pas visité 
            donc pour être SUR qu'il ne passe pas de u à v directement on va mettre la distance a MAX et donc il va 
            aller chercher un chemin dont tout les sommets sont visité 
            et ces le cas seulement quand i est != 0 car le premier indices et 0 et on peut passer de 0 and v directement
            ce n'est pas un soucis
            """


            if i != 0:    
                mini_graph[ind_v][ind_u] = MAX_INT
                mini_graph[ind_u][ind_v] = MAX_INT

            dist_matrix, predecessor = dijkstra(csgraph=csr_array(mini_graph), directed=False, indices=ind_u, return_predecessors=True)
            
            total_predecessors.append(mapp_predecessor(n,tmp_visited,predecessor))
            G_prime[i][j] = dist_matrix[  ind_v ]
            G_prime[j][i] = dist_matrix[  ind_v ]

    return G_prime,total_predecessors

def nearest_neighbor(G_star,G_prime,blockages,predecessor,U):
    
    n = len(G_prime)
    visited = [False] * n
    path = [0]
    visited[0] = True
    current = 0
    U = list(U)[1:] # {0, 2, 3} we skip the first one it is visited

    while len(U) != 0:
        next_vertex = -1
        min_dist = float('inf')

        # FROM THE SHORTEST PATH USED BEFORE 
        min_index = np.argmin(G_prime[current])
        min_value = np.min(G_prime[current])

        # we have to compare with the direct distance from current to the min_index 
        direct_dist = G_star[current][U[min_index]]
        #if min_value > direct_dist and blockages[]

        break

    """
    while len(path) < n:
        next_vertex = -1
        min_dist = float('inf')
        
        for i in range(n):
            if not visited[i]:
                  graph[current][i] < min_dist:
                min_dist = graph[current][i]
                next_vertex = i
                
        if next_vertex == -1:break
            
        path.append(next_vertex)
        visited[next_vertex] = True
        current = next_vertex
    """
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
    
    print("PATH: ",path_in_letters)
    # Create shortcut path
    G_star, U, P1 = shortcut(matrix, christophides_path, blockages)
    
    # Create compressed graph G'
    G_prime,pred = compress(G_star, U, matrix)

    P2 = nearest_neighbor(G_star,G_prime,blockages,pred,U)
    
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
        ["D", "E"],["E","D"],["E","C"],["C","E"],
    ]

    final_path = apply_cnn_to_routes(routes, blockages)
    #print(f"Path: {final_path}")

