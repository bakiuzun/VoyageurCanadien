from christofides import apply_christophides
import christofides
from utils import transform_to_matrix,get_path_in_letters

routes = {
    'A': {'A':0, 'B': 1, 'C':2,'D': 1,'E':1},
    'B': {'A': 1, 'B':0, 'C':1, 'D': 2, 'E': 1},
    'C': {'A': 2, 'B':1, 'C':0, 'D': 1, 'E': 1},
    'D': {'A': 1, 'B':2, 'C':1, 'D': 0, 'E': 1},
    'E': {'A': 1, 'B':1, 'C':1, 'D': 1, 'E': 0},
}

blockages = [
    ['D', 'E']
]


def find_next_vertice_after_block(from_source, blocked_dest,blockages,path,i):
    
    while [from_source,blocked_dest] in blockages:
        if i + 1 == len(path):
            # no link to the last vertice
            return -1 
        i += 1
        blocked_dest = path[i]

    next_vertice = i
    return next_vertice


def find_intermediaire_vertice(from_source,dest,path,visited):
    
    source_index = path.index(from_source)
    dest_index = path.index(dest)

    if source_index < dest_index:
        # Normal case: source comes before dest
        subpath = path[source_index + 1 : dest_index]
    else:
        # Circular case: dest comes before source
        subpath = path[source_index + 1 :] + path[:dest_index]
    
    intermediaire = [v for v in subpath if v in visited]
    
    return intermediaire # list 


def find_next_vertice_with_neighbor(from_source,blocked_dest,blockages,visited):

    # check if i can go from source to one neighbor if yes then check if i can go from this neighbor to the blocked_dest
    for visited_vertice in visited:
        if [from_source,visited_vertice] not in blockages and [visited_vertice,blocked_dest] not in blockages:
            # done 
            return visited_vertice
        
    # we can't find a way to go the the blocked dest by taking one visited 
    # maybe we should take multiple visited vertice before
    return -1 


def first_iteration(path,blockages):

    P1_cr = []

    source = path[0]
    P1_cr.append(source)
    
    i = 1
    while i != len(path):
        dest = path[i]
        
        if [source,dest] in blockages:
            i = find_next_vertice_after_block(source,dest,blockages,path,i) 

            if i == -1:break # we can't go to the last vertice

            dest = path[i]
        i += 1 
        P1_cr.append(dest)
        source = dest
    
    return i,P1_cr



def apply_routage_cyclique(routes,blockages):
    matrix = transform_to_matrix(routes)
    christofides_path = apply_christophides(matrix)
    path = get_path_in_letters(christofides_path,routes)
    

    # check blocages
    path = ['A','B','C','D']
    #blockages = [ ['A','B'],['A','C'], ['B','C'] ]
    blockages = [ ['B','C'],['D','C'],['A','C']  ]
    initial_path = path 

    complete_path = []

    i,used_path = first_iteration(path,blockages)

    non_visited = [item for item in path if item not in used_path]
    visited = used_path

    complete_path += visited

    # remaining iteration are done here because it is the same principal
    #while len(NonVisited) != len(initial_path):
    
    if used_path[-1] == path[i-1]:
        # même sens     
        source = path[i-1] # last vertice
        path = non_visited # new path 

        i = 0
        
        print("PATH = ",path)
        while i <= len(path):
            dest = path[i]
            if [source,dest] in blockages:
                # intermediaire 
                intermediaire_vertices =  find_intermediaire_vertice(source,dest,initial_path,visited)
                next_vertice = find_next_vertice_with_neighbor(source,dest,blockages,intermediaire_vertices) 
                
                # could not find intermediare vertex
                if next_vertice == -1:
                    i += 2 # skip the next dest 
                else:
                    i += 1
                    complete_path.append(next_vertice)
                    complete_path.append(dest)
                    visited.append(dest)

            else:
                complete_path.append(dest)
                visited.append(dest)
                i += 1 
            
            source = dest
        
        print('COMPLETE PATH = ',complete_path)
        print('VISITED = ',visited )
    else: # i == -1, means we couldn't go to the last vertice we should change the order 
        pass
    
    
    
    # racordement du dernier sommet au sommet de départ 

apply_routage_cyclique(routes,blockages)
