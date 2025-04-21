import numpy as np
import networkx as nx

def ACPM(graph,s=0):
    """
    Minimum Spanning Tree
    Prim's algorithm
    param:
        graph: 2D complete array
        s: the index at which we should start. It can be random, but good to specify for debugging
    """
    couts = np.array([float('inf')] * len(graph))
    predecesor = [-1] * len(graph)

    # commence du sommet 0, résultat toujours pareil
    couts[s] = 0

    Q = np.arange(len(graph))

    while len(Q) != 0:
        # sommet de coût minimal qui est dans Q
        min_vertex =  np.argmin(couts[Q])
        idx_vertex = Q[min_vertex]

        # on le supprime, il est marqué il sera plus utilisé
        Q = np.delete(Q,min_vertex)
        edges = graph[idx_vertex,Q]

        for i in range(len(edges)):
            if edges[i] < couts[Q[i]]:
                couts[Q[i]] = edges[i]
                predecesor[Q[i]] = idx_vertex

    return np.array(predecesor)


def compute_impair_vertices(acpm_tree):
    """
    calculer l'ensemble de degrés impaires
    param:
        acpm_graph: 1D array, il contient le prédécéseur de chaque sommet
        sachant que le sommet de départ à la valeur de -1

    return:
        les sommets de degrés impaires
    """

    """
    on utilise un arbre couvrant donc forcément chaque sommet
    à un 'prédéceseur' donc on initialise à 1 apart le sommet
    de 'départ'
    """
    # on utilise un arbre couvrant donc forcément
    degrees = np.array([1] * len(acpm_tree))
    degrees[np.argwhere(acpm_tree == -1)] = 0

    for i in range(len(acpm_tree)):

        # pour chaque sommet si dans la liste des prédécéseurs
        # il y a ce sommet alors on incrémente son degré
        to_add = np.sum(acpm_tree == i)
        degrees[i] += to_add

    odd_vertices =  np.argwhere(degrees % 2 == 1).flatten()

    return odd_vertices

def minimum_weight_matching(graph,vertices):
    """
    bossom algorithm to find the minimum weight matching 
    param:
        graph 2D array where i,j is the weight for the edge (i,j)
        vertices: index of the vertex of odd degree

    return 2D array e.g [[0,3], [2,4]] means 0 and 3 are linked, 2 and 4 are linked and it's the minimum weight 
    """
    G = nx.Graph()
    G.add_nodes_from(vertices)
    for source in vertices:
        for dest in vertices:
            G.add_edge(source, dest, weight=graph[source,dest])
    
    ret = nx.min_weight_matching(G)

    return np.array(list(ret),dtype=int)
    

def unite_matching_acpm(matching_M,acpm_T,graph):
    """
    We should combine the edges of the ACPM and the minimum_weight_matching
    it will be our final graph that we will use for the Euler tour
    """
    res = [[] for _ in range(len(graph))]

    # e.g
    # [[4], [4], [4], [4], [0, 1, 2, 3]]
    # the first vertice has the 4th vertice as an edge
    # the second one also as well as the third one, the last one has 0 1 2 3 has edge
    for i in range(len(graph)):
        # acpm_T[i] will always be one value
        if acpm_T[i] != -1:
            res[i].append( (acpm_T[i]) )
            res[acpm_T[i]].append( (i) )

    # on suppose que ces 2 sommet pour un couplage a chaque fois, sa peut-être faux
    for i in matching_M:
        vertice1,vertice2 = i
        res[vertice1].append( (vertice2) )
        res[vertice2].append( (vertice1) )
    return res


def euler_tour(list_adj,start_vertex=0):
    """
    euler tour
    param:
        list adj we get this from unite_matching_acpm method
        e.g [[(4), (1)], [(4), (0)], [(4), (3)], [(4), (2)], [(0), (1), (2), (3)]]
        the first vertice can go to the vertice 4 and 1,
        the second vertice can go to the vertice 4 and 0, .... it's symetric

    return:
        euler tour with potentially a cycle
    """

    tour = []
    stack = [start_vertex]

    while stack:
        u = stack[-1]

        if len(list_adj[u]) > 0:
            v = list_adj[u].pop()
            list_adj[v].remove(u)
            stack.append(v)
        else:
            tour.append(stack.pop())


    return tour[::-1]

def remove_repeated_vertices_euleur(tour):
    """
    after performing euleur tour we should remove the repeated vertices
    as we can only pass one time for each vertices
    param:
        tour: the tour founded by the euleur algo

    return:
        same tour with removed repeated vertices

    e.g  [4, 3, 2, 4, 1, 0, 4]
    start at vertice 4 then go to 3 - 2 - 4 (repeated should be removed) ....
    after calling this method: [4, 3, 2, 1, 0, 4]
    """
    visited = []
    idx_to_remove = []
    for i in range(0,len(tour)-1):
        if tour[i] not in visited:
            visited.append(tour[i])
        else:
            # it has already been visited we should branch we the next one
            idx_to_remove.append(i)

    tour = np.array(tour)
    tour = np.delete(tour,idx_to_remove)

    return tour.tolist()


def apply_christophides(arbre):
    """
    application of the christophides algorithme 
    param:
        arbre: 2D numpy array where the index (i,j) represent the weight of the edge (i,j) source i -  dest j 

    return the christophides output,e.g [0,1,4,3,2,0] means we should start at 0 go to 1,4,3,2 then finish at 0 
    """
    # https://en.wikipedia.org/wiki/Christofides_algorithm

    acpm_graph = ACPM(arbre,s=0)
    
    odd_vertices = compute_impair_vertices(acpm_graph)
    
    minimum_matching_vertices = minimum_weight_matching(arbre,odd_vertices)

    acpm_union_min_vertices = unite_matching_acpm(minimum_matching_vertices,acpm_graph,arbre)

    tour = euler_tour(acpm_union_min_vertices,start_vertex=0)

    tour = remove_repeated_vertices_euleur(tour)

    return tour


arbre = np.array([[0,1,2,1,1],
                    [0,0,1,2,1],
                    [0,0,0,1,1],
                    [0,0,0,0,1],
                    [0,0,0,0,0],
                 ])


# test celui du td
"""
arbre = np.array([  [0,2,1,3,2],
                    [0,0,1,2,3],
                    [0,0,0,2,3],
                    [0,0,0,0,2],
                    [0,0,0,0,0],
                 ])
"""

arbre = arbre + arbre.T # symmetric
#print('Solution: ',apply_christophides(arbre))

