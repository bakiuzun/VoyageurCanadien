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
    initial_path = path 

    i,used_path = first_iteration(path,blockages)

    non_visited = [item for item in path if item not in used_path]
    visited = used_path

    # remaining iteration are done here because it is the same principal
    #while len(NonVisited) != len(initial_path):
    
    if i == len(used_path):
        # même sens     
        source = path[i-1] # last vertice
        path = non_visited # new path 

        i = 1 
        while i != len(path):
            dest = path[i]
            
            if [source,dest] in blockages:
                # find a way with the neighboor 
                intermediaire_vertex = find_next_vertice_with_neighbor(source,dest,blockages,visited) 


                # could not find intermediare vertex
                if intermediaire_vertex == -1:

                    # we will have 2 times i += 1 so we skip it
                    i += 2 # skip the next dest 

                else:
                    visited.append(dest)

            else:
                visited.append(dest)
                i += 1 
                source = dest




    else: # i == -1, means we couldn't go to the last vertice we should change the order 
        pass




apply_routage_cyclique(routes,blockages)
