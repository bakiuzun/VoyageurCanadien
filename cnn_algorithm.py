import numpy as np
from christofides import apply_christophides
from utils import transform_to_matrix, get_path_in_letters,get_blockages_in_int,calculate_cost
from scipy.sparse import csr_array
from scipy.sparse.csgraph import dijkstra
import sys 

MAX_INT = sys.maxsize


def mapp_predecessor(n,tmp_visited,predecessor):
    """
    when using Dijkstra we give it only a mini-matrice which means the vertice at the first
    index might not be the first vertice of the whole matrice the one that contains every vertice
    so when a list of predecessor [2,1,4] probably the 2 represent another index in the whole matrice and 
    we just want to map it 
    param:
        n: number of vertices in total 
        tmp_visited: the visited vertice + 2 of the unvisited vertice 
        predecessor: a list that contain the predecessors to go from U to any other vertice 
    """
    mapped_predecessor = np.full(n, -1, dtype=int)  # -1 pour les non-visités
    
    for k, pred in enumerate(predecessor):
        if pred != -9999:  # -9999 est la valeur par défaut de scipy pour aucun prédécesseur
            mapped_predecessor[tmp_visited[k]] = tmp_visited[pred]   
    return mapped_predecessor

def retrieve_path_from_pred(source_ind,dest_ind,predecessor):
    """
    this method give us the path from source to dest using the predecessors 
    for example we might have source = A, dest = E, predecessor B,C,D 
    this would give us A-B-C-D-E
    param:
        source_ind: the index at which we start
        dest_ind: the index at which we end 
        predecessor: a list that contains the predecessors to go from source to any other vertice
    """
    i = dest_ind
    p = []

    while i != source_ind:
        p.append(int(i)) # i is a np.int64 
        i = predecessor[i]
    return p[::-1]

def get_reverse_predecessor(n, original_predecessor, u_idx, v_idx):
    """
    this function is used in Dijkstra when we found a path from U to V we also want to know 
    the path from V to U, 
    param:
        n: the numbers of vertices in total
        original_predecessor: the predecessors to go from u to v 
        u_idx: the index at which we have u
        v_idx: the index at which we have v
    """
    # Step 1: Get the path u → v
    path_u_to_v = []
    current = v_idx
    while current != u_idx:
        path_u_to_v.append(current)
        current = original_predecessor[current]
    path_u_to_v.append(u_idx)
    path_u_to_v = path_u_to_v[::-1]  

    path_v_to_u = path_u_to_v[::-1]  
    
    reverse_predecessor = np.full(n, -1, dtype=int)

    for i in range(1, len(path_v_to_u)):
        node = path_v_to_u[i]
        pred = path_v_to_u[i-1]
        reverse_predecessor[node] = pred

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
    
    print(f"Shortcut Eb: {Eb}")
    return G_star, U, P1

def compress(G_star, U):
    """
    Create multigraph G' from G* and U
    For each pair of vertices in U, find shortest path using only known edges
    param:
        G_star: modified matrice after the shortcut 
        U: the list of unvisited vertices
    """
    Us = list(U)  
    n = len(G_star)
    G_prime = [[0] * len(Us) for _ in range(len(Us))]

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
            total_predecessors[v,u] = get_reverse_predecessor(n,mapped_original_index,u,v)
            
            G_prime[i][j] = dist_matrix[ ind_v ]
            G_prime[j][i] = dist_matrix[  ind_v ]

    return G_prime,total_predecessors


def nearest_neighbor(G_star,G_prime,blockages,predecessor,U):
    """
    NN algorithm 
    param:
        G_star: modified matrice after the shortcut 
        G_prime: a list that contains the cost for each of the unvisited vertices 
        blockages: list that represent the blockages 
        predecessor: a list that contains the predecessor for a given path 
        for example maybe to go to the vertice C from A we just take the vertice B and D (found in Djisktra) 
        U: the list of unvisited vertices
    """
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
        cost = min_dist
        taken_path = []
        
        if [U[current],U[min_index]] in blockages:
            G_star[U[current]][U[min_index]] = MAX_INT
            G_star[U[min_index]][U[current]] = MAX_INT
            # si il y a un blockages alors forcement on va utiliser le chemin donner par le compress
            # car celui ci passe par des chemin déjà visité ces garantie
            taken_path = retrieve_path_from_pred(U[current],U[min_index],predecessor[U[current],U[min_index]])
        else:
            # il y a pas de blockage et le chemin directe et mieux que celui trouvé dans compress
            if min_dist >= direct_dist:
                # we don't use the shortest path 
                cost = direct_dist
                taken_path = [U[min_index]]
            else:
                # ceci ne dois pas être possible car INEGALITE TRIANGULAIRE
                # il y a pas de blockages mais ce chemin et mieux que le chemin actuel
                taken_path = retrieve_path_from_pred(U[current],U[min_index],predecessor[U[current],U[min_index]]) 
                

        # le plus cours chemin + le chemin direct est bloqué 
        # on stop l'algortihme il faut au moins un chemin vers ce sommet 
        if cost == MAX_INT:
            raise Exception(f"Aucun chemin a été trouvé pour accéder le sommet {U[min_dist]} depuis {U[current]} ")
        
        path.extend(taken_path)
        visited[min_index] = True
        current = min_index

    if G_prime[current][0] == MAX_INT: # Blockage 
        # on retourne en arriere comme dans shortcut
        return_path = path[::-1][1:]  
        path.extend(return_path)
    else:
        path.extend(retrieve_path_from_pred(source_ind=U[current],dest_ind=0,predecessor=predecessor[U[current],0]))

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
    
    P2 = []
    # Create compressed graph G'
    if len(U) > 1: # some vertices hasn't been visited
        G_prime,pred = compress(G_star, U)
        P2 = nearest_neighbor(G_star,G_prime,blockages,pred,U)
    
    
    print(f'P1: {P1}')
    print(f'P2: {P2}')
    final_path = P1 + P2
    return final_path

"""
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

"""

