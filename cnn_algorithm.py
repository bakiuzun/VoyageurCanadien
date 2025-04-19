import numpy as np
from christofides import apply_christophides
from utils import transform_to_matrix, get_path_in_letters,get_blockages_in_int,calculate_cost
from scipy.sparse import csr_array
from scipy.sparse.csgraph import dijkstra
import sys 

MAX_INT = sys.maxsize


def mapp_predecessor(n,tmp_visited,predecessor):

    mapped_predecessor = np.full(n, -1, dtype=int)  # -1 pour les non-visités
    
    for k, pred in enumerate(predecessor):
        if pred != -9999:  # -9999 est la valeur par défaut de scipy pour aucun prédécesseur
            mapped_predecessor[tmp_visited[k]] = tmp_visited[pred]   
    return mapped_predecessor

def retrieve_path_from_pred(source_ind,dest_ind,predecessor):
    
    i = dest_ind
    p = []

    while i != source_ind:
        p.append(int(i)) # i is a np.int64 
        i = predecessor[i]
    return p[::-1]

def get_reverse_predecessor(n, tmp_visited, original_predecessor, u_idx, v_idx):
    # Step 1: Get the path u → v
    path_u_to_v = []
    current = v_idx
    while current != u_idx:
        path_u_to_v.append(current)
        current = original_predecessor[current]
    path_u_to_v.append(u_idx)
    path_u_to_v = path_u_to_v[::-1]  

    path_v_to_u = path_u_to_v[::-1]  
    
    # Step 3: Build predecessor array for v → u
    reverse_predecessor = np.full(n, -1, dtype=int)
    for i in range(1, len(path_v_to_u)):
        node = path_v_to_u[i]
        pred = path_v_to_u[i-1]
        reverse_predecessor[tmp_visited[node]] = tmp_visited[pred]

    return reverse_predecessor

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
    
    return G_star, U, P1

def compress(G_star, U):
    """
    Create multigraph G' from G* and U
    For each pair of vertices in U, find shortest path using only known edges
    """
    Us = list(U)  
    n = len(G_star)
    G_prime = [[MAX_INT] * len(Us) for _ in range(len(Us))]

    visited_vertices = list(set(range(n)) - set(Us))  # V \ Us 
    total_predecessors  = {}

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

            dist_matrix, predecessor = dijkstra(csgraph=csr_array(mini_graph), 
                                                directed=False, 
                                                indices=ind_u, 
                                                return_predecessors=True)
            
            mapped_original_index = mapp_predecessor(n,tmp_visited,predecessor)
            
            total_predecessors[u,v] = mapped_original_index
            total_predecessors[v,u] = get_reverse_predecessor(n,tmp_visited,mapped_original_index,u,v)
            
            G_prime[i][j] = dist_matrix[ ind_v ]
            G_prime[j][i] = dist_matrix[  ind_v ]

    return G_prime,total_predecessors


def nearest_neighbor(G_star,G_prime,blockages,predecessor,U):
    
    G_prime = np.array(G_prime)
    n = len(G_prime)
    visited = [False] * n
    path = [] # we don't include the 0 we don't need 
    visited[0] = True
    current = 0
    U = list(U) # {0, 2, 3} we skip the first one it is visited
    
    while sum(visited) != n:
        min_dist = float('inf')

        for i in range(n):
            if G_prime[current][i] < min_dist and visited[i] == False:
                min_index = i
                min_dist = G_prime[current][i]

        # we have to compare with the direct distance from current to the min_index 

        direct_dist = G_star[U[current]][U[min_index]]
        if [U[current],U[min_index]] in blockages:
            G_star[U[current]][U[min_index]] = MAX_INT
            G_star[U[min_index]][U[current]] = MAX_INT
            # si il y a un blockages alors forcement on va utiliser le chemin donner par le compress
            # car celui ci passe par des chemin déjà visité ces garantie

            path.extend(retrieve_path_from_pred(U[current],U[min_index],predecessor[U[current],U[min_index]]))
        else:
            # il y a pas de blockage et le chemin directe et mieux que celui trouvé dans compress
            if min_dist >= direct_dist:
                # we don't use the shortest path 
                path.append(U[min_index])
            else:
                # il y a pas de blockages mais ce chemin et mieux que le chemin actuel
                path.extend(retrieve_path_from_pred(U[current],U[min_index],predecessor[U[current],U[min_index]]))

        visited[min_index] = True
        current = min_index

    path.extend(retrieve_path_from_pred(source_ind=U[current],dest_ind=0,predecessor=predecessor[U[current],0]))
    # we now know every blocked trajectory 
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
    blockages = get_blockages_in_int(blockages,routes)
    
    # Create shortcut path
    G_star, U, P1 = shortcut(matrix, christophides_path, blockages)
    
    # Create compressed graph G'
    G_prime,pred = compress(G_star, U)

    P2 = nearest_neighbor(G_star,G_prime,blockages,pred,U)
    
    final_path = P1 + P2
    return final_path

if __name__ == "__main__":
    routes = {
        'A': {'A':0, 'B': 1, 'C':2,'D': 1,'E':1},
        'B': {'A': 1, 'B':0, 'C':1, 'D': 4, 'E': 1},
        'C': {'A': 2, 'B':1, 'C':0, 'D': 1, 'E': 1},
        'D': {'A': 1, 'B':4, 'C':1, 'D': 0, 'E': 1},
        'E': {'A': 1, 'B':1, 'C':1, 'D': 1, 'E': 0},
    }

    blockages = [
        ["D", "E"],["E","C"]
    ]
    
    final_path = apply_cnn_to_routes(routes, blockages)
    
    f = get_path_in_letters(solution=final_path,base_tuple=routes)
    print(f"Final Path: {f}")
    print(f"Cost: {calculate_cost(f,routes)}")

