from christofides import apply_christophides
from utils import transform_to_matrix,get_path_in_letters,create_symmetric_blockage,calculate_cost
routes = {
    'A': {'A':0, 'B': 1, 'C':2,'D': 1,'E':1},
    'B': {'A': 1, 'B':0, 'C':1, 'D': 2, 'E': 1},
    'C': {'A': 2, 'B':1, 'C':0, 'D': 1, 'E': 1},
    'D': {'A': 1, 'B':2, 'C':1, 'D': 0, 'E': 1},
    'E': {'A': 1, 'B':1, 'C':1, 'D': 1, 'E': 0},
}

blockages = [
    ['D', 'E'],['E','D']
]

def find_next_vertice_after_block(from_source, blocked_dest,blockages,path,i):
    """
    for the first iteration if there is a blockage from one source vertice to a destination then
    we should look to the next vertice that should be taken using the 'path'
    e.g
    path = ['A','B','C','D','E']
    blockages = [['C','D']]
    the algorithm will go from A to B, from B to C then enter this function that will try to go from C to D, then from C to E as it is not blocked
    it will return i which represent the index of the vertice that we are going to take
    if the blockages was [ ['C','D'],['C','E] ] then it would go from A to B, B to C, from C it would try D (but blockage) then try E (blockage) then
    there is no more vertice so we return -1
    param:
        from_source: string that represent a 'Vertice'
        blocked_dest: string that represent a 'Vertice
        blockages: 2D array of string [ ['A','B'],['A,'C] ] means A and B, A and C are blocked
        path: the christofides path that should be followed
        i: the index at which we should start if we have the path ['A','B','C','D','E'] with blockages [['C','D']] then the i is equal to 3 (index of D )

    return the index that repesent the next vertice we should take, if no vertice available return -1

    """
    while [from_source,blocked_dest] in blockages:
        if i + 1 == len(path):
            # no link to the last vertice
            return -1
        i += 1
        blocked_dest = path[i]

    next_vertice = i
    return next_vertice


def find_intermediaire_vertice(from_source,dest,path,visited):
    """
    method that return the vertice between one source and a destination
    if we have ['A','B','C','D','E'] with blockages [['C','D']] and the source is E
    the goal is to reach C then D or the D then C depending on the direction. so from E to C we have intermediate vertices (A and B)
    then we filter A and B to retain only those that has been visited, so the intermediate vertice is already visited.
    param:
        from_source: string that represent a 'Vertice'
        dest: string that represent a 'Vertice
        path: 1D array representing the christofides path, it can be reversed depending on the direction
        visited: 1D array representing the visited vertices
    return:
        the intermediate vertices between source and dest
    """
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


def find_next_vertice_with_intermediate(from_source,blocked_dest,blockages,intermediates_vertices):
    """
    we use the intermediate vertex to know if it's possible to access the blocked dest from the source using one intermediate vertex
    if possible we return this vertex, else return - 1

    param:
        from_source: string that represent a 'Vertice'
        dest: string that represent a 'Vertice
        blockages: 2D array representing the blockages, e.g [ ['A','B'] ]
        visited:
        path: 1D array representing the christofides path, it can be reversed depending on the direction
        intermediates_vertices: intermediates vertices between source and blocked dest

    """
    # check if i can go from source to one neighbor if yes then check if i can go from this neighbor to the blocked_dest
    for intermed_vertice in intermediates_vertices:
        if [from_source,intermed_vertice] not in blockages and [intermed_vertice,blocked_dest] not in blockages:
            # done
            return intermed_vertice

    # we can't find a way to go the the blocked dest by taking one intermediate vertex
    return -1


def apply_first_iteration(path,blockages):
    """
    the first iteration of the algortihm
    path: 1D christofides path
    blockages: 2D array representing the blockages
    e.g path
    path = ['A','B','C','D','E']
    blockages = [['C','D']]
    it will go from A to B then B to C, then as there is a blockage between C and D it will go from C to E
    retuned path = ['A','B','C','E']
    """
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



def apply_iteration_m(path_to_take,source,visited_vertices,initial_path,blockages):
    """
    implementation of the iteration after the first iteration and before the last one
    in this function we try to take the path given by 'path_to_take' each time we are blocked between one source and a destination
    we search intermediate vertices to go from the source to the intermediate and from the intermediate to the destination
    if there is no intermediate vertices capable of doing so we just change the dest to the next one and keep the same source.

    param:
        path_to_take: 1D array that gives the path we should follow,e.g [A,B,C,D,F]
        source: string, representing the source vertex that we should start from
        visited_vertices: 1D array representing the vertices already visited, we use it for the intermediate function e.g [A,D,C]...
        initial_path: 1D array we use this to know the direction and also all the vertices that we can have
        for example if i have an initial path of [A,B,C,D,E,F,G,H] and with the first iteration i took A,B,C,D,H then i need
        [E,F,G] to go from H to E I need to know what are the vertices between H and E and this information is given thanks the initial path that contains
        the A,B,C and D if the direction is inversed then I should go from H to [G,F,E]
        blockages: 2D arrays containing all the blockages [ [A,B],[E,D] ] ..

    return the path we have been able to take and the updated visited vertices

    """
    taken_path = []
    i = 0

    while i < len(path_to_take):

        dest = path_to_take[i]
        if [source,dest] in blockages:
                    # intermediaire
            intermediaire_vertices =  find_intermediaire_vertice(source,dest,initial_path,visited_vertices)
            next_vertice = find_next_vertice_with_intermediate(source,dest,blockages,intermediaire_vertices)

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

    return taken_path,visited_vertices

def apply_last_iteration(goal_vertice,source,visited_vertices,blockages):
    """
    for the last iteration all the vertices have been visited if from the source we can't atteign the goal
    then we find an intermediate vertice regardless of it's positions it can be anywhere on the graph and we are sure that it existe
    because every vertices has been visited before this step so at least one vertice will be able to go to the dest
    param:
        goal_vertice string Vertice it represent the first vertice on the christofides path
        source: vertice we are currently in and we try to go to the goal
        visited_vertices: this list contains all the vertices
        blockages: 2D blockages
    return the goal vertice if there is no blockages, else return the intermediate vertice + the goal vertice
    """
    if [source,goal_vertice] in blockages:
        # find with intermediate
        next_vertice = find_next_vertice_with_intermediate(source,goal_vertice,blockages,visited_vertices)
        return [next_vertice,goal_vertice]
    else:
        return [goal_vertice] # we go directly


def get_non_visited_vertice(all_vertice,visited_vertice):
    """
    method to get the non visited vertice
    param:
        all_vertice: 1D array that contains every vertex
        visited_vertice: 1D array that contains the visited vertices
    return:
        vertex that is not in visited_vertice list
    """
    return [item for item in all_vertice if item not in visited_vertice]


def reverse_order(last_visited,non_visited_vertices,initial_path):
    """
    this function is used to reverse the order of the vertices
    we first locate where the last visited vertice is in the initial path
    then we take the left and right part of the path and reverse them
    param:
        last_visited: the last vertice we have visited
        non_visited_vertices: the vertices that are not visited
        initial_path: the initial path that we should follow
    return:
        the reversed order of the vertices
    """
    last_visited_index = initial_path.index(last_visited)

    left = initial_path[:last_visited_index]
    right = initial_path[last_visited_index+1:]

    left = [v for v in left if v in non_visited_vertices]
    right = [v for v in right if v in non_visited_vertices]

    
    return list(reversed(left)) + list(reversed(right))



def apply_routage_cyclique(routes,blockages):
    """
    main function for the CR algorithm
    param:
        routes: dict containing for each vertex a dict with the destination and the cost e.g {'V1': {'V1':0,'V2':1,'V3':3...},'V2': {'V1':1,'V2':0}..}
        blockages: 2D array containing all the blockages e.g [ [A,B],[A,C] ] if we can't take the edge A-B nor A-C

    return CR algorithm output, from one source

    """
    matrix = transform_to_matrix(routes)
    christofides_path = apply_christophides(matrix)
    path_to_take = get_path_in_letters(christofides_path,routes)

    path_to_take = path_to_take[:-1] # i just remove the last vertice because it is equal to the first one
    initial_path = path_to_take
    last_vertice = path_to_take[0] # last and first are equal

    blockages = create_symmetric_blockage(blockages)
    
    # first iteration
    taken_path = apply_first_iteration(path_to_take,blockages)
    visited_vertices = taken_path
    complete_path = taken_path.copy() # this is the results
    non_visited_vertices = get_non_visited_vertice(initial_path,taken_path)

    # m iteration
    print(f"P1: {path_to_take} ")
    print(f"Pcr: {taken_path} ")
    print(f"Unvisited Vertices: {non_visited_vertices}\n")

    m = 2
    while len(non_visited_vertices) != 0:
        
        if len(taken_path) > 0 and  taken_path[-1] == path_to_take[-1]:
            initial_path = initial_path

        else: # i == -1, means we couldn't go to the last vertice we should change the order
            non_visited_vertices =  reverse_order(complete_path[-1],non_visited_vertices,initial_path)
            initial_path = list(reversed(initial_path))
            
        print(f"P{m}: {[complete_path[-1]] + non_visited_vertices} ")
        taken_path,visited_vertices =  apply_iteration_m(path_to_take=non_visited_vertices,
                                                         source=complete_path[-1],
                                                         visited_vertices=visited_vertices,
                                                         initial_path=initial_path,
                                                         blockages=blockages)
        
        print(f"Pcr: {[complete_path[-1]] + taken_path}")
        complete_path += taken_path
        path_to_take = non_visited_vertices

        non_visited_vertices  = get_non_visited_vertice(initial_path,visited_vertices)
        
        
        print(f"Unvisited Vertices: {non_visited_vertices}\n")
        m += 1

    # last iteration
    taken_path = apply_last_iteration(goal_vertice=last_vertice,
                                      source=complete_path[-1],
                                      visited_vertices=visited_vertices,
                                       blockages=blockages)

    print(f"P{m}: {[complete_path[-1]] + [last_vertice]}")
    print(f"Pcr: {[complete_path[-1]] + taken_path}\n")

    complete_path += taken_path

    return complete_path


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

# Example usage
complete_path = apply_routage_cyclique(routes,blockages)
print(f"Complete path: {complete_path}")
print(f"Cost: {calculate_cost(complete_path,base_tuple=routes) }")



