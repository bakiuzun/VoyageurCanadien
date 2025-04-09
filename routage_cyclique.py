from christofides import apply_christophides
from utils import transform_to_matrix,get_path_in_letters,construct_example_path

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


def apply_first_iteration(path,blockages):
    ### we just apply christofides 
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
    
    return P1_cr



def apply_iteration_m(path_to_take,taken_path,visited_vertices,initial_path,blockages):
    # même sens     
    
    source = taken_path[-1] # last vertice that we used 
    taken_path = []
    
    i = 0
            
    while i < len(path_to_take):
                
        dest = path_to_take[i]
        if [source,dest] in blockages:
                    # intermediaire 
            intermediaire_vertices =  find_intermediaire_vertice(source,dest,initial_path,visited_vertices)
            
            next_vertice = find_next_vertice_with_neighbor(source,dest,blockages,intermediaire_vertices) 
                    
                    # could not find intermediare vertex, blockage everywhere to this vertex
            if next_vertice == -1:
                # same source , different dest
                i += 1 
            else:
                i += 1
                taken_path.append(next_vertice)
                taken_path.append(dest)
                visited_vertices.append(dest)
                source = dest

        else:
            i += 1 
            taken_path.append(dest)
            visited_vertices.append(dest)        
            source = dest

    return path_to_take,taken_path,visited_vertices


def get_non_visited_vertice(all_vertice,visited_vertice):
    return [item for item in all_vertice if item not in visited_vertice]


def apply_routage_cyclique(routes,blockages):
    routes = construct_example_path()
    matrix = transform_to_matrix(routes)
    christofides_path = apply_christophides(matrix)
    path_to_take = get_path_in_letters(christofides_path,routes)
    
    path_to_take = path_to_take[:-1] # i just remove the last vertice because it is equal to the first one 
    initial_path = path_to_take
    
    path_to_take = [f'V{i+1}' for i in range(0,16) ] # V1 - V16
    initial_path = path_to_take
    first_direction = initial_path.copy()
    last_vertice = path_to_take[0] 
    blockages = [ ['V3','V4'],['V3','V5'],
                  ['V7','V8'],
                  ['V9','V10'],
                  ['V12','V13'],
                  ['V12','V14'],
                  ['V16','V4'],
                  ['V4','V5'],
                  ['V8','V10'],
                  ['V13','V14'],
                  ['V13','V10'],
                  ['V13','V12'],
                  ['V10','V5'],
                  ['V10','V9'],
                  ['V10','V8'],
                  ['V5','V4'],
                  ['V5','V14'],
                  ['V5','V3'],
                  ['V14','V1']
                 ] 
    
    # first iteration 
    taken_path = apply_first_iteration(path_to_take,blockages)
    visited_vertices = taken_path
    complete_path = taken_path.copy() # this is the results
    non_visited_vertices = get_non_visited_vertice(initial_path,taken_path)

    # m iteration 
    while len(non_visited_vertices) != 0:
        if taken_path[-1] == path_to_take[-1]:
            initial_path = initial_path
            
        else: # i == -1, means we couldn't go to the last vertice we should change the order 
            initial_path = list(reversed(initial_path))
            last_one = non_visited_vertices[-1]
            non_visited_vertices = list(reversed(non_visited_vertices[:-1])) + [last_one]
    
         # we to the operation in the same direction
        path_to_take,taken_path,visited_vertices =  apply_iteration_m(non_visited_vertices,taken_path,
                                                                      visited_vertices,
                                                                      initial_path,blockages)
        complete_path += taken_path
        non_visited_vertices  = get_non_visited_vertice(initial_path,visited_vertices)
        
    # last iteration 
    path_to_take,taken_path,visited_vertices =  apply_iteration_m([last_vertice],taken_path,
                                                                      visited_vertices,
                                                                      first_direction,blockages)
    complete_path += taken_path
    
    print(complete_path)
# racordement du dernier sommet au sommet de départ 

apply_routage_cyclique(routes,blockages)
