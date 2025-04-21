import numpy as np
import random 

def transform_to_matrix(tuple_graph):
    """Transform a tuple to matrix form"""
    matrix = [[0 for _ in range(len(tuple_graph))] for _ in range(len(tuple_graph))]
    for i, node in enumerate(tuple_graph):
        for j, neighbor in enumerate(tuple_graph):
            matrix[i][j] = tuple_graph[node][neighbor]
    return np.array(matrix)


def create_symmetric_blockage(blockages):
    """takes a blockages list and make it symmetric """
    ret = blockages.copy()
    for block in blockages:
        s,d = block
        ret.append([d,s])

    return ret
def get_blockages_in_int(blockages,base_tuple):
    res = []
    keys = list(base_tuple.keys())
    k = {}
    for i in range(len(keys)):k[keys[i]] = i
    for i in range(len(blockages)):
        sr,dest = blockages[i]
        res.append([k[sr],k[dest]])
        res.append([k[dest],k[sr]])
    return res

def get_path_in_letters(solution,base_tuple):
    """
    we use this method because when we apply christofides it gives us a solution for e.g
    [0, 3, 4, 2, 1, 0] from vertex 0 to 3 to 4 .... but we want it in letters A to B to D ...
    so we have to use the base_tuple to know exactly which is the first vertex the second one etc
    for example if we have as a solution [0, 3, 4, 2, 1, 0]
    and the base_tuple
    'A': {'A':0, 'B': 1, 'C':2,'D': 1,'E':1},
    'B': {'A': 1, 'B':0, 'C':1, 'D': 2, 'E': 1},
    'C': {'A': 2, 'B':1, 'C':0, 'D': 1, 'E': 1},
    'D': {'A': 1, 'B':2, 'C':1, 'D': 0, 'E': 1},
    'E': {'A': 1, 'B':1, 'C':1, 'D': 1, 'E': 0},

    the returned results:
        ['A', 'D', 'E', 'C', 'B', 'A']
    """
    res = []
    keys = list(base_tuple.keys())

    for i in range(len(solution)):
        res.append(keys[solution[i]])
    return res



def calculate_cost(solution,base_tuple):
    """calculate the cost of taking a path """
    cost = 0 
    for i in range(len(solution)-1):
        s = solution[i]
        d = solution[i+1]
        cost += base_tuple[s][d]

    return cost

def construct_example_path():
    vertices = [f"V{i+1}" for i in range(0,16)]
    
    routes = {}

    for i in range(len(vertices)):
        depart = vertices[i]
        l = {}
        for j in range(len(vertices)):
            
            arriver = vertices[j]
            cout = int(np.abs(j - i))
            l[arriver] = cout

        routes[depart] = l
            
    return routes



def construct_alea_graph(nb_vertices=None,nb_blockages=None):

    if nb_vertices is None:
        nb_vertices = random.randint(50, 100)
    if nb_blockages is None:
        nb_blockages = 10*nb_vertices
    graph = {}
    
    cost_matrix = np.zeros((nb_vertices, nb_vertices), dtype=int)
    
    for i in range(nb_vertices):
        for j in range(i + 1, nb_vertices):
            cost_matrix[i][j] = random.randint(1, 100)
            cost_matrix[j][i] = cost_matrix[i][j] 
    
    for k in range(nb_vertices):
        for i in range(nb_vertices):
            for j in range(nb_vertices):
                if cost_matrix[i][j] > cost_matrix[i][k] + cost_matrix[k][j]:
                    cost_matrix[i][j] = cost_matrix[i][k] + cost_matrix[k][j]
    
    for i in range(nb_vertices):
        v = f"V{i}"
        e = {}
        for j in range(nb_vertices):
            e[f"V{j}"] = int(cost_matrix[i][j])
        graph[v] = e
        
    blockages = []
    nb_blockages = 10*nb_vertices
    for i in range(nb_blockages):
        source = random.randint(0,nb_vertices-1)

        dest = random.randint(0,nb_vertices-1)
        if dest == source:
        
            while dest == source or [f"V{source}",f"V{dest}"] in blockages:
                dest = random.randint(0,nb_vertices-1)
        
        blockages.append([f"V{source}",f"V{dest}"])

    return graph,blockages